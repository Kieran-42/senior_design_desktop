import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray 
from control_rear_right_leg import RearRightLegController
from control_rear_left_leg import RearLeftLegController

def main(args=None):
    rclpy.init(args=args)
    left = RearLeftLegController()
    right = RearRightLegController()

    try:
        left.run_demo()
        right.run_demo()
    finally:
        left.destroy_node()
        right.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()