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
        parameters=[{'robot_description': Command(['xacro ', urdf_path])}]
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

    # 4. Spawners for ros2_control (These will now find the service once Gazebo starts)
    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    wheel_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["wheel_controller"],
    )

    # Create one spawner for each leg controller
    leg_spawners = [
        Node(package="controller_manager", executable="spawner", arguments=[f"{side}_leg_controller"])
        for side in ["rear_right", "rear_left", "front_right", "front_left"]
    ]

    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn_robot,
        joint_state_broadcaster,
        wheel_controller,
        *leg_spawners
    ])