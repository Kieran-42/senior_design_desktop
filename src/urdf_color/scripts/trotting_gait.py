#!/usr/bin/env python3
#
# Trotting gait controller for urdf_color (non-block model).
# Diagonal pair trot (FL+BR vs FR+BL) with triangle interpolation
# for swing trajectories. Foot targets solved with 2-link planar IK.
#
# Link lengths measured from URDF joint origins:
#   L1 (upper leg) = 0.179378 m  (joint_XX2 -> joint_XX3 Y-offset)
#   L2 (lower leg) = 0.16 m      (joint_XX3 -> joint_XX4 Y-offset)
#

import math
import time
import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

# link lengths from URDF (joint offsets)
L1 = 0.179378   # upper leg: joint_XX2 -> joint_XX3
L2 = 0.16       # lower leg: joint_XX3 -> joint_XX4

# gait tuning
GAIT_PERIOD  = 0.6      # sec per full cycle
X_STEP       = 0.10     # half-step length (m)
SWING_HEIGHT = 0.05     # foot lift height (m)
Z_GROUND     = -0.30    # nominal foot height below hip joint (m)

CONTROL_HZ = 50


def lerp(p0, p1, alpha):
    return (1.0 - alpha) * p0 + alpha * p1


def interpolate_triangle(t, touchdown, stand, liftoff, mid_swing):
    """
    Walk through 4 waypoints in a triangle path.
    t in [0,1): stance phase first half, stance second half, swing up, swing down.
    """
    t = t % 1.0
    if t < 0.25:
        return lerp(touchdown, stand, t / 0.25)
    elif t < 0.50:
        return lerp(stand, liftoff, (t - 0.25) / 0.25)
    elif t < 0.75:
        return lerp(liftoff, mid_swing, (t - 0.50) / 0.25)
    else:
        return lerp(mid_swing, touchdown, (t - 0.75) / 0.25)


def ik_2link(x_target, y_target, knee_direction=-1):
    """
    2-link planar IK. x = forward, y = up (foot targets have negative y).
    Returns (q1, q2) or None if out of reach.
    """
    r_sq = x_target**2 + y_target**2
    r = math.sqrt(r_sq)

    if r > (L1 + L2) or r < abs(L1 - L2):
        # clamp to workspace boundary
        r = max(abs(L1 - L2) + 0.001, min(r, L1 + L2 - 0.001))
        r_sq = r * r
        scale = r / math.sqrt(x_target**2 + y_target**2)
        x_target *= scale
        y_target *= scale

    cos_q2 = (r_sq - L1**2 - L2**2) / (2.0 * L1 * L2)
    cos_q2 = max(-1.0, min(1.0, cos_q2))
    q2 = knee_direction * math.acos(cos_q2)   # -1 for back, 1 for forward

    alpha = math.atan2(x_target, -y_target)
    beta  = math.atan2(L2 * math.sin(q2), L1 + L2 * math.cos(q2))
    q1 = alpha - beta

    return q1, q2


def compute_leg_waypoints(z_ground, x_step, swing_height):
    """Build the 4 waypoints for one leg."""
    touchdown = np.array([ x_step / 2.0, z_ground])
    stand     = np.array([ 0.0,          z_ground])
    liftoff   = np.array([-x_step / 2.0, z_ground])
    mid_swing = np.array([ 0.0,          z_ground + swing_height])
    return touchdown, stand, liftoff, mid_swing


def gait_targets(phase, x_step, z_ground, swing_height):
    """Get foot targets for all 4 legs at a given phase."""
    wp = compute_leg_waypoints(z_ground, x_step, swing_height)

    targets = {}
    # diagonal pair A
    targets['front_left']  = interpolate_triangle(phase, *wp)
    targets['back_right']  = interpolate_triangle(phase, *wp)
    # diagonal pair B (offset half cycle)
    targets['front_right'] = interpolate_triangle((phase + 0.5) % 1.0, *wp)
    targets['back_left']   = interpolate_triangle((phase + 0.5) % 1.0, *wp)
    return targets


class TrottingGaitNode(Node):

    LEG_NAMES = ['front_left', 'front_right', 'back_left', 'back_right']

    def __init__(self):
        super().__init__('trotting_gait_node')

        self.leg_pubs = {}
        for leg in self.LEG_NAMES:
            topic = f'/{leg}_leg_controller/commands'
            self.leg_pubs[leg] = self.create_publisher(Float64MultiArray, topic, 10)

        self.gait_period  = GAIT_PERIOD
        self.x_step       = X_STEP
        self.swing_height = SWING_HEIGHT
        self.z_ground     = Z_GROUND

        self.t0 = time.time()
        self.timer = self.create_timer(1.0 / CONTROL_HZ, self.control_callback)

        self.get_logger().info(
            f'Trotting gait started  period={self.gait_period}s  '
            f'step={self.x_step}m  swing_h={self.swing_height}m  '
            f'z_ground={self.z_ground}m'
        )

    def control_callback(self):
        elapsed = time.time() - self.t0
        phase = (elapsed % self.gait_period) / self.gait_period

        targets = gait_targets(phase, self.x_step, self.z_ground, self.swing_height)

        for leg in self.LEG_NAMES:
            x_foot, y_foot = targets[leg]
            
            # Set all legs to bend forward (knee-style)
            knee_dir = 1
            result = ik_2link(x_foot, y_foot, knee_direction=knee_dir)
            
            if result is None:
                self.get_logger().warn(f'{leg}: IK unreachable ({x_foot:.4f}, {y_foot:.4f})')
                continue

            q1, q2 = result
            msg = Float64MultiArray()
            msg.data = [0.0, q1, q2]    # [hip_abduction, upper_leg, lower_leg]
            self.leg_pubs[leg].publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TrottingGaitNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # zero all joints on exit
        for leg in TrottingGaitNode.LEG_NAMES:
            msg = Float64MultiArray()
            msg.data = [0.0, 0.0, 0.0]
            node.leg_pubs[leg].publish(msg)
        node.get_logger().info('Gait stopped, joints zeroed.')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
