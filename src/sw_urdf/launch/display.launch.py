import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_share = get_package_share_directory('mechakaldr_assembly_urdf')
    urdf_file = os.path.join(pkg_share, 'urdf', 'MECHAKALDR_AssemblySW2URDF.urdf')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    rviz_config = os.path.join(pkg_share, 'config', 'display.rviz')

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
        ),
    ])
