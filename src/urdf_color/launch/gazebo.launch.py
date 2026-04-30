import os
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_share = get_package_share_directory('urdf_color')
    xacro_file = os.path.join(pkg_share, 'urdf', 'urdf_color.urdf.xacro')

    # Launch arguments
    camera_name_arg = DeclareLaunchArgument(
        'camera_name', default_value='zedm',
        description='Name of the ZED camera'
    )
    camera_model_arg = DeclareLaunchArgument(
        'camera_model', default_value='zedm',
        description='Model of the ZED camera'
    )
    use_zed_localization_arg = DeclareLaunchArgument(
        'use_zed_localization', default_value='true',
        description='Whether to use ZED localization'
    )

    camera_name = LaunchConfiguration('camera_name')
    camera_model = LaunchConfiguration('camera_model')
    use_zed_localization = LaunchConfiguration('use_zed_localization')

    # Process Xacro
    robot_description_content = Command([
        'xacro ', xacro_file,
        ' camera_name:=', camera_name,
        ' camera_model:=', camera_model,
        ' use_zed_localization:=', use_zed_localization,
    ])

    # Also tell Gz where to look for model:// URIs (install/share parent)
    gz_resource_path = os.path.dirname(pkg_share)

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': True,
        }],
    )

    # Launch Gazebo Harmonic (gz_sim)
    world_file = os.path.join(pkg_share, 'worlds', 'robodog_world.sdf')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch', 'gz_sim.launch.py',
            )
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items(),
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

    # RViz
    rviz_config_file = os.path.join(pkg_share, 'config', 'display.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': True}]
    )

    # Bridge Gazebo topics to ROS 2
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/world/robodog_world/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
        ],
        remappings=[
            ('/world/robodog_world/clock', '/clock'),
        ],
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
        camera_name_arg,
        camera_model_arg,
        use_zed_localization_arg,
        robot_state_publisher,
        gazebo,
        spawn_robot,
        rviz,
        bridge,
        joint_state_broadcaster,
        front_right_leg,
        front_left_leg,
        back_right_leg,
        back_left_leg,
    ])
