import os
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_share = get_package_share_directory('urdf_color')
    urdf_file = os.path.join(pkg_share, 'urdf', 'urdf_color.urdf')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    # Resolve package:// URIs to file:// so Gazebo Harmonic can find meshes
    robot_description = robot_description.replace(
        'package://urdf_color/',
        'file://' + pkg_share + '/',
    )

    # Resolve $(find ...) so gz_ros2_control can locate the controller YAML
    robot_description = robot_description.replace(
        '$(find urdf_color)',
        pkg_share,
    )

    # Also tell Gz where to look for model:// URIs (install/share parent)
    gz_resource_path = os.path.dirname(pkg_share)

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
    )

    # Launch Gazebo Harmonic (gz_sim)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch', 'gz_sim.launch.py',
            )
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    # Spawn the robot in Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'urdf_color',
            '-z', '0.5',
        ],
        output='screen',
    )

    # Bridge Gazebo clock to ROS 2
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen',
    )

    # Controller spawners
    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    front_right_leg = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["front_right_leg_controller"],
    )

    front_left_leg = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["front_left_leg_controller"],
    )

    back_right_leg = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["back_right_leg_controller"],
    )

    back_left_leg = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["back_left_leg_controller"],
    )

    return LaunchDescription([
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', gz_resource_path),
        robot_state_publisher,
        gazebo,
        spawn_robot,
        clock_bridge,
        joint_state_broadcaster,
        front_right_leg,
        front_left_leg,
        back_right_leg,
        back_left_leg,
    ])
