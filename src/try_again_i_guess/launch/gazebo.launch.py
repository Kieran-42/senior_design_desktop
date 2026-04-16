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
    pkg_share = get_package_share_directory('try_again_i_guess')
    urdf_file = os.path.join(pkg_share, 'urdf', 'try_again_i_guess.urdf')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    # Resolve package:// URIs to file:// so Gazebo Harmonic can find meshes
    robot_description = robot_description.replace(
        'package://try_again_i_guess/',
        'file://' + pkg_share + '/',
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
            '-name', 'try_again_i_guess',
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

    return LaunchDescription([
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', gz_resource_path),
        robot_state_publisher,
        gazebo,
        spawn_robot,
        clock_bridge,
    ])
