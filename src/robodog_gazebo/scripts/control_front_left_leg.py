#!/usr/bin/env python3
"""
Interactive controller for the front left leg joints.

Joints (in order):
  1. front_left_base_hip_joint      (revolute, position)
  2. front_left_hip_1_hip_2_joint   (revolute, position)
  3. front_left_tibia_paw_joint     (revolute, position)

Usage:
  ros2 run robodog_gazebo control_front_left_leg
  -- or --
  python3 control_front_left_leg.py
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class FrontLeftLegController(Node):
    JOINT_NAMES = [
        'front_left_base_hip_joint',
        'front_left_hip_1_hip_2_joint',
        'front_left_tibia_paw_joint',
    ]

    def __init__(self):
        super().__init__('front_left_leg_controller_node')
        self.publisher = self.create_publisher(
            Float64MultiArray,
            '/front_left_leg_controller/commands',
            10,
        )
        # Current target positions (radians)
        self.positions = [0.0, 0.0, 0.0]
        self.get_logger().info('Front left leg controller ready.')
        self.print_help()

    def print_help(self):
        print('\n========== Front Left Leg Controller ==========')
        print('Joints:')
        for i, name in enumerate(self.JOINT_NAMES):
            print(f'  [{i}] {name}')
        print()
        print('Commands:')
        print('  <hip_base> <hip12> <tibia_paw>  — Set all 3 joint positions (radians)')
        print('  home                             — Move all joints to 0.0')
        print('  demo                             — Run a simple demo sequence')
        print('  help                             — Show this help')
        print('  quit / q                         — Exit')
        print('================================================\n')

    def publish_positions(self):
        msg = Float64MultiArray()
        msg.data = self.positions
        self.publisher.publish(msg)
        self.get_logger().info(
            f'Published: base_hip={self.positions[0]:.3f}, '
            f'hip12={self.positions[1]:.3f}, '
            f'tibia_paw={self.positions[2]:.3f}'
        )

    def run_demo(self):
        """Run a simple sequence of poses."""
        import time

        poses = [
            ([0.0, 0.0, 0.0], 'Home position'),
            ([0.5, 0.0, 0.0], 'Hip base forward'),
            ([0.5, 0.3, 0.0], 'Hip 1-2 rotated'),
            ([0.5, 0.3, 0.5], 'Tibia-paw bent'),
            ([0.0, 0.5, -0.5], 'Mixed pose'),
            ([-0.3, -0.3, 0.3], 'Reverse pose'),
            ([0.0, 0.0, 0.0], 'Back to home'),
        ]

        for positions, label in poses:
            print(f'  >> {label}: {positions}')
            self.positions = list(positions)
            self.publish_positions()
            time.sleep(2.0)

        print('Demo complete.\n')

    def interactive_loop(self):
        try:
            while rclpy.ok():
                user_input = input('leg> ').strip().lower()

                if not user_input:
                    continue
                elif user_input in ('quit', 'q', 'exit'):
                    break
                elif user_input == 'help':
                    self.print_help()
                elif user_input == 'home':
                    self.positions = [0.0, 0.0, 0.0]
                    self.publish_positions()
                elif user_input == 'demo':
                    self.run_demo()
                else:
                    try:
                        values = [float(v) for v in user_input.split()]
                        if len(values) != 3:
                            print('Error: Please provide exactly 3 values (or type "help").')
                            continue
                        self.positions = values
                        self.publish_positions()
                    except ValueError:
                        print(f'Unknown command: "{user_input}". Type "help" for options.')

        except (KeyboardInterrupt, EOFError):
            print('\nExiting...')


def main(args=None):
    rclpy.init(args=args)
    node = FrontLeftLegController()

    try:
        node.interactive_loop()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
