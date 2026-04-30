import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_share = get_package_share_directory('urdf_color')
    xacro_file = os.path.join(pkg_share, 'urdf', 'urdf_color.urdf.xacro')

    use_zed_localization_arg = DeclareLaunchArgument(
        'use_zed_localization', default_value='true',
        description='Whether to use ZED localization'
    )
    use_zed_localization = LaunchConfiguration('use_zed_localization')

    robot_description_content = Command([
        'xacro ', xacro_file,
        ' use_zed_localization:=', use_zed_localization,
    ])

    rviz_config = os.path.join(pkg_share, 'config', 'display.rviz')

    return LaunchDescription([
        use_zed_localization_arg,
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description_content}],
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
