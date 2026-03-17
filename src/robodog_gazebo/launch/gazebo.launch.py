import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration

def generate_launch_description():
    package_name = 'robodog_gazebo'
    
    # Path to your URDF (Skeleton)
    urdf_path = os.path.join(get_package_share_directory(package_name), 'urdf', 'robodog_skeleton.urdf')
    
    # 1. Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro ', urdf_path]),
            'use_sim_time': True
        }]
    )

    # 2. Launch Gazebo Harmonic (gz_sim)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    # 3. Spawn the robot in Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'robodog', '-z', '0.5'],
        output='screen',
    )

    # 4. Bridge Gazebo clock to ROS 2
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen',
    )

    # 5. Spawners for ros2_control
    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    diff_drive_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_drive_controller"],
    )

    # Leg controller spawners
    rear_right_leg = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["rear_right_leg_controller"],
    )

    rear_left_leg = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["rear_left_leg_controller"],
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

    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn_robot,
        clock_bridge,
        joint_state_broadcaster,
        diff_drive_controller,
        rear_right_leg,
        rear_left_leg,
        front_right_leg,
        front_left_leg,
    ])