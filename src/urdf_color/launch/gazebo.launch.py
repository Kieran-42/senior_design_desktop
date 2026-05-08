import os
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    DeclareLaunchArgument,
    RegisterEventHandler,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration, TextSubstitution
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
        'use_zed_localization', default_value='false',
        description='Whether to use ZED localization'
    )
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_share, 'worlds', 'robodog_world.sdf'),
        description='Path to the Gazebo world/SDF file to launch'
    )
    world_name_arg = DeclareLaunchArgument(
        'world_name',
        default_value='robodog_world',
        description='Name inside the selected world file, used for Gazebo world-scoped topics'
    )
    gz_resource_path_arg = DeclareLaunchArgument(
        'gz_resource_path',
        default_value=os.path.dirname(pkg_share),
        description='Gazebo resource path for model:// includes'
    )

    camera_name = LaunchConfiguration('camera_name')
    camera_model = LaunchConfiguration('camera_model')
    use_zed_localization = LaunchConfiguration('use_zed_localization')
    world = LaunchConfiguration('world')
    world_name = LaunchConfiguration('world_name')
    gz_resource_path = LaunchConfiguration('gz_resource_path')
    world_clock_topic = [
        TextSubstitution(text='/world/'),
        world_name,
        TextSubstitution(text='/clock'),
    ]

    # Process Xacro
    robot_description_content = Command([
        'xacro ', xacro_file,
        ' camera_name:=', camera_name,
        ' camera_model:=', camera_model,
        ' use_zed_localization:=', use_zed_localization,
    ])

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
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch', 'gz_sim.launch.py',
            )
        ),
        launch_arguments={'gz_args': ['-r ', world]}.items(),
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


    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        arguments=[
            [
                TextSubstitution(text='/world/'),
                world_name,
                TextSubstitution(text='/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'),
            ],
            '/zed/zed_node/rgb/image_rect_color/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/zed/zed_node/rgb/image_rect_color/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/zed/zed_node/rgb/image_rect_color/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/zed/zed_node/rgb/image_rect_color/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/zed/zed_node/rgb/image_raw_color@sensor_msgs/msg/Image[gz.msgs.Image',
            '/zed/zed_node/right/image_rect_color@sensor_msgs/msg/Image[gz.msgs.Image',
            '/zed/zed_node/right/image_rect_color/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/zed/zed_node/right/image_raw_color@sensor_msgs/msg/Image[gz.msgs.Image',
            '/zed/zed_node/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/zed/zed_node/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/zed/zed_node/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/model/urdf_color/pose@geometry_msgs/msg/PoseArray[gz.msgs.Pose_V',
        ],
        remappings=[
            (world_clock_topic, '/clock'),
            ('/zed/zed_node/rgb/image_rect_color/image', '/zed/zed_node/rgb/image_rect_color'),
            ('/zed/zed_node/rgb/image_rect_color/depth_image', '/zed/zed_node/depth/depth_registered'),
            ('/zed/zed_node/rgb/image_rect_color/points', '/zed/zed_node/point_cloud/cloud_registered'),
            ('/zed/zed_node/rgb/image_raw_color', '/zed/zed_node/rgb_raw/image_raw_color'),
            ('/zed/zed_node/right/image_rect_color', '/zed/zed_node/right/image_rect_color'),
            ('/zed/zed_node/right/image_raw_color', '/zed/zed_node/right_raw/image_raw_color'),
            ('/zed/zed_node/tf', '/tf'),
            ('/model/urdf_color/pose', '/zed/zed_node/pose'),
        ],
        parameters=[{'use_sim_time': True}],
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
        camera_name_arg,
        camera_model_arg,
        use_zed_localization_arg,
        world_arg,
        world_name_arg,
        gz_resource_path_arg,
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', gz_resource_path),
        SetEnvironmentVariable('GZ_SIM_MODEL_PATH', gz_resource_path),
        SetEnvironmentVariable('GAZEBO_MODEL_PATH', gz_resource_path),
        robot_state_publisher,
        gazebo,
        spawn_robot,
        bridge,
        joint_state_broadcaster,
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster,
                on_exit=[front_right_leg],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=front_right_leg,
                on_exit=[front_left_leg],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=front_left_leg,
                on_exit=[back_right_leg],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=back_right_leg,
                on_exit=[back_left_leg],
            )
        ),
    ])
