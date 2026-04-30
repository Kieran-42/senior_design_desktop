import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('urdf_color')
    nav2_params_path = os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    rtabmap_params_path = os.path.join(pkg_share, 'config', 'rtabmap.yaml')

    # 1. Include the simulation launch
    # This starts Gazebo, Robot State Publisher, RViz, and the Gz-ROS bridge
    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'gazebo.launch.py')
        )
    )

    # 2. Motor Command Node (Gait Controller)
    motor_command = Node(
        package='urdf_color',
        executable='motor_command.py',
        name='motor_command_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
        remappings=[('cmd_vel', '/cmd_vel_smoothed')]
    )

    # 3. Twist Mux (Prioritize Teleop over Nav2)
    twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        name='twist_mux',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'topics': {
                'navigation': {
                    'topic': '/cmd_vel_nav',
                    'timeout': 0.5,
                    'priority': 10
                },
                'teleop': {
                    'topic': '/cmd_vel_teleop',
                    'timeout': 0.5,
                    'priority': 100
                }
            }
        }],
        remappings=[('cmd_vel_out', '/cmd_vel')]
    )

    # 4. Teleop Terminal
    from launch.actions import ExecuteProcess, TimerAction
    teleop = ExecuteProcess(
        cmd=['gnome-terminal', '--', 'ros2', 'run', 'teleop_twist_keyboard', 'teleop_twist_keyboard', '--ros-args', '-r', 'cmd_vel:=/cmd_vel_teleop'],
        output='screen'
    )

    # 5. RTAB-Map SLAM
    rtabmap = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        name='rtabmap',
        output='screen',
        parameters=[rtabmap_params_path],
        remappings=[
            ('rgb/image', '/zed/zed_node/rgb/image_rect_color'),
            ('depth/image', '/zed/zed_node/depth/depth_registered'),
            ('rgb/camera_info', '/zed/zed_node/rgb/image_rect_color/camera_info'),
            ('odom', '/zed/zed_node/odom'),
            ('imu', '/zed/zed_node/imu/data'),
        ],
        arguments=['-d'] # Delete database before starting (fresh map)
    )

    # 6. Nav2 Stack
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'params_file': nav2_params_path,
            'use_sim_time': 'True',
        }.items()
    )

    return LaunchDescription([
        simulation,
        # Wait 5 seconds for simulation to stabilize before starting gait
        TimerAction(period=5.0, actions=[motor_command]),
        twist_mux,
        teleop,
        rtabmap,
        nav2
    ])
