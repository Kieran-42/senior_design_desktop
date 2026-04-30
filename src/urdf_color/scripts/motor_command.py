#!/usr/bin/env python3
#
# Motor command node -- translates cmd_vel into leg joint commands.
# Mimics how an Arduino motor controller would interpret velocity
# commands: linear.x drives forward/backward walking speed,
# angular.z drives turning by differentiating left/right step lengths.
#
# When cmd_vel is zero the robot holds a standing pose.
# When cmd_vel arrives the robot trots with step size proportional
# to the requested speed.
#

import math
import signal
import time
import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import Twist

# ── link lengths from URDF (same as trotting_gait) ──
L1 = 0.179378   # upper leg
L2 = 0.16       # lower leg

# ── gait tuning ──
GAIT_PERIOD    = 0.2     # seconds per full walking cycle
MAX_X_STEP     = 0.10    # max half-step length at full speed (m)
SWING_HEIGHT   = 0.05    # foot lift during swing (m)
Z_GROUND       = -0.30   # nominal foot height below hip (m)

# mapping from cmd_vel to gait parameters
MAX_LINEAR_VEL  = 0.5    # m/s — cmd_vel.linear.x at which step = MAX_X_STEP
MAX_ANGULAR_VEL = 1.0    # rad/s — cmd_vel.angular.z at which full differential

CONTROL_HZ  = 50
CMD_TIMEOUT = 0.5  # seconds without a cmd_vel before stopping


def lerp(p0, p1, alpha):
    return (1.0 - alpha) * p0 + alpha * p1


def interpolate_triangle(t, touchdown, stand, liftoff, mid_swing):
    """Walk through 4 waypoints in a triangle path (same as trotting_gait)."""
    t = t % 1.0
    if t < 0.25:
        return lerp(touchdown, stand, t / 0.25)
    elif t < 0.50:
        return lerp(stand, liftoff, (t - 0.25) / 0.25)
    elif t < 0.75:
        return lerp(liftoff, mid_swing, (t - 0.50) / 0.25)
    else:
        return lerp(mid_swing, touchdown, (t - 0.75) / 0.25)


def ik_2link(x_target, y_target, knee_direction=1):
    """2-link planar IK (same as trotting_gait)."""
    r_sq = x_target**2 + y_target**2
    r = math.sqrt(r_sq)

    if r > (L1 + L2) or r < abs(L1 - L2):
        r = max(abs(L1 - L2) + 0.001, min(r, L1 + L2 - 0.001))
        r_sq = r * r
        scale = r / math.sqrt(x_target**2 + y_target**2)
        x_target *= scale
        y_target *= scale

    cos_q2 = (r_sq - L1**2 - L2**2) / (2.0 * L1 * L2)
    cos_q2 = max(-1.0, min(1.0, cos_q2))
    q2 = knee_direction * math.acos(cos_q2)

    alpha = math.atan2(x_target, -y_target)
    beta  = math.atan2(L2 * math.sin(q2), L1 + L2 * math.cos(q2))
    q1 = alpha - beta

    return q1, q2


def compute_leg_waypoints(z_ground, x_step, swing_height):
    """Build the 4 waypoints for one leg given a signed step size."""
    touchdown = np.array([ x_step / 2.0, z_ground])
    stand     = np.array([ 0.0,          z_ground])
    liftoff   = np.array([-x_step / 2.0, z_ground])
    mid_swing = np.array([ 0.0,          z_ground + swing_height])
    return touchdown, stand, liftoff, mid_swing


class MotorCommandNode(Node):

    LEG_NAMES = ['front_left', 'front_right', 'back_left', 'back_right']

    def __init__(self):
        super().__init__('motor_command_node')

        self._stopping = False

        # publishers — one per leg controller
        self.leg_pubs = {}
        for leg in self.LEG_NAMES:
            topic = f'/{leg}_leg_controller/commands'
            self.leg_pubs[leg] = self.create_publisher(Float64MultiArray, topic, 10)

        # cmd_vel subscriber
        self.create_subscription(Twist, '/cmd_vel', self._cmd_vel_cb, 10)

        # latest velocity command + timestamp
        self.linear_x  = 0.0
        self.angular_z = 0.0
        self.last_cmd_time = 0.0

        # gait phase tracking
        self.t0 = time.time()
        self.is_walking = False

        # control loop
        self.timer = self.create_timer(1.0 / CONTROL_HZ, self._control_loop)

        self.get_logger().info(
            'Motor command node started — waiting for /cmd_vel'
        )

    # ── callbacks ──

    def _cmd_vel_cb(self, msg: Twist):
        self.linear_x  = msg.linear.x
        self.angular_z = msg.angular.z
        self.last_cmd_time = time.time()

        if not self.is_walking and (abs(self.linear_x) > 0.01 or abs(self.angular_z) > 0.01):
            # reset phase so the gait starts from a clean cycle
            self.t0 = time.time()
            self.is_walking = True
            self.get_logger().info(
                f'Walking — lin={self.linear_x:.2f} ang={self.angular_z:.2f}'
            )

    def _control_loop(self):
        if self._stopping:
            self._publish_standing_pose()
            self.timer.cancel()
            self.get_logger().info('Stopped — legs at standing pose.')
            raise SystemExit

        # timeout: if no cmd_vel for a while, treat as zero velocity
        now = time.time()
        if (now - self.last_cmd_time) > CMD_TIMEOUT:
            self.linear_x  = 0.0
            self.angular_z = 0.0

        # decide if we should walk or stand
        moving = abs(self.linear_x) > 0.01 or abs(self.angular_z) > 0.01

        if not moving:
            if self.is_walking:
                self.is_walking = False
                self.get_logger().info('Standing — cmd_vel is zero')
            self._publish_standing_pose()
            return

        # ── compute per-leg step sizes (Arduino-style differential) ──
        # normalize inputs
        speed_frac = max(-1.0, min(1.0, self.linear_x / MAX_LINEAR_VEL))
        turn_frac  = max(-1.0, min(1.0, self.angular_z / MAX_ANGULAR_VEL))

        # base step from forward speed
        base_step = speed_frac * MAX_X_STEP

        # turn differential: positive angular.z = turn left
        # left legs get shorter steps, right legs get longer steps
        turn_offset = turn_frac * MAX_X_STEP * 0.5

        steps = {
            'front_left':  base_step - turn_offset,
            'back_left':   base_step - turn_offset,
            'front_right': base_step + turn_offset,
            'back_right':  base_step + turn_offset,
        }

        # gait phase
        elapsed = now - self.t0
        phase = (elapsed % GAIT_PERIOD) / GAIT_PERIOD

        # compute foot targets & publish
        for leg in self.LEG_NAMES:
            step = steps[leg]

            # if the step is effectively zero for this leg, use a tiny step
            # to avoid degenerate waypoints
            if abs(step) < 0.005:
                step = 0.005 if step >= 0 else -0.005

            wp = compute_leg_waypoints(Z_GROUND, step, SWING_HEIGHT)

            # diagonal pair phasing: FL+BR vs FR+BL
            if leg in ('front_left', 'back_right'):
                leg_phase = phase
            else:
                leg_phase = (phase + 0.5) % 1.0

            foot = interpolate_triangle(leg_phase, *wp)
            x_foot, y_foot = foot

            q1, q2 = ik_2link(x_foot, y_foot, knee_direction=1)

            # hip abduction stays at 0 (straight down)
            msg = Float64MultiArray()
            msg.data = [0.0, q1, q2]
            self.leg_pubs[leg].publish(msg)

    def _publish_standing_pose(self):
        """Command all legs to the neutral standing position."""
        stand = np.array([0.0, Z_GROUND])
        q1, q2 = ik_2link(stand[0], stand[1], knee_direction=1)
        for leg in self.LEG_NAMES:
            msg = Float64MultiArray()
            msg.data = [0.0, q1, q2]
            self.leg_pubs[leg].publish(msg)

    def request_stop(self):
        if not self._stopping:
            self._stopping = True
            self.get_logger().info('Ctrl+C — finishing up...')


def main(args=None):
    rclpy.init(args=args, signal_handler_options=rclpy.SignalHandlerOptions.NO)

    node = MotorCommandNode()
    signal.signal(signal.SIGINT, lambda *_: node.request_stop())

    try:
        rclpy.spin(node)
    except SystemExit:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
