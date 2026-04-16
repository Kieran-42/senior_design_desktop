#!/usr/bin/env python3
#
# Quick test for the diff_drive_controller - publishes cmd_vel at 10Hz.
#

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
import signal
import sys


class DiffDriveTest(Node):
    def __init__(self):
        super().__init__('diff_drive_test_node')
        self.pub = self.create_publisher(TwistStamped, '/diff_drive_controller/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.publish_cmd)
        self.get_logger().info('Publishing TwistStamped cmd_vel at 10Hz (linear.x=-0.2)')

    def publish_cmd(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.twist.linear.x = -0.2
        msg.twist.angular.z = 0.0
        self.pub.publish(msg)

    def stop(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        self.pub.publish(msg)
        self.get_logger().info('Stopped.')


def main(args=None):
    rclpy.init(args=args)
    node = DiffDriveTest()

    def on_sigint(sig, frame):
        node.stop()
        node.destroy_node()
        rclpy.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, on_sigint)
    rclpy.spin(node)


if __name__ == '__main__':
    main()
