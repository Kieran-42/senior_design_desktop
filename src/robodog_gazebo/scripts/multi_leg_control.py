#!/usr/bin/env python3
#
# Move multiple legs at the same time using a single ROS 2 node.
#

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import time

class MultiLegController(Node):
    def __init__(self):
        super().__init__('multi_leg_controller_node')

        self.pubs = {
            'front_left':  self.create_publisher(Float64MultiArray, '/front_left_leg_controller/commands', 10),
            'front_right': self.create_publisher(Float64MultiArray, '/front_right_leg_controller/commands', 10),
            'rear_left':   self.create_publisher(Float64MultiArray, '/rear_left_leg_controller/commands', 10),
            'rear_right':  self.create_publisher(Float64MultiArray, '/rear_right_leg_controller/commands', 10),
        }

        self.get_logger().info('Multi-leg controller ready.')

    def move_legs(self, leg_positions):
        """Publish positions to multiple legs at once.
        leg_positions: dict mapping leg name -> [hip_base, hip12, tibia_paw]
        """
        for leg, pos in leg_positions.items():
            if leg not in self.pubs:
                self.get_logger().warn(f'Unknown leg: {leg}')
                continue
            msg = Float64MultiArray()
            msg.data = [float(p) for p in pos]
            self.pubs[leg].publish(msg)
            self.get_logger().info(f'{leg}: {pos}')

    def run_demo(self):
        self.get_logger().info('Starting demo...')

        poses = [
            ({'front_left': [0.5, 0.3, 0.5], 'rear_right': [0.5, 0.3, 0.5]}, 'Diagonal lift'),
            ({'front_left': [0.0, 0.0, 0.0], 'rear_right': [0.0, 0.0, 0.0]}, 'Home'),
            ({'front_right': [-0.5, -0.3, -0.5], 'rear_left': [-0.5, -0.3, -0.5]}, 'Other diagonal'),
            ({'front_right': [0.0, 0.0, 0.0], 'rear_left': [0.0, 0.0, 0.0]}, 'Home'),
        ]

        for leg_data, label in poses:
            self.get_logger().info(f'Pose: {label}')
            self.move_legs(leg_data)
            time.sleep(2.0)

        self.get_logger().info('Demo done.')

def main(args=None):
    rclpy.init(args=args)
    node = MultiLegController()

    try:
        node.run_demo()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
