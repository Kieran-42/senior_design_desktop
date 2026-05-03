import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    # Get the launch directory
    pkg_share = get_package_share_directory('urdf_color')

    namespace = LaunchConfiguration('namespace')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    params_file = LaunchConfiguration('params_file')

    lifecycle_nodes = [
        'controller_server',
        'planner_server',
        'behavior_server',
        'bt_navigator'
    ]

    # Map fully qualified names to relative ones so remappings work as expected
    remappings = [('/tf', 'tf'),
                  ('/tf_static', 'tf_static')]

    # Create our own temporary YAML files that include substitutions
    param_substitutions = {
        'use_sim_time': use_sim_time,
        'autostart': autostart
    }

    configured_params = RewrittenYaml(
        source_file=params_file,
        root_key=namespace,
        param_rewrites=param_substitutions,
        convert_types=True)

    return LaunchDescription([
        # Set env var to print messages to stdout immediately
        DeclareLaunchArgument(
            'namespace',
            default_value='',
            description='Top-level namespace'),

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'),

        DeclareLaunchArgument(
            'autostart', default_value='true',
            description='Automatically startup the nav2 stack'),

        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg_share, 'config', 'nav2_params.yaml'),
            description='Full path to the ROS2 parameters file to use'),

        Node(
            package='nav2_controller',
            executable='controller_server',
            output='screen',
            parameters=[configured_params, {'use_sim_time': use_sim_time}],
            remappings=remappings),

        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[configured_params, {'use_sim_time': use_sim_time}],
            remappings=remappings),

        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[configured_params, {'use_sim_time': use_sim_time}],
            remappings=remappings),

        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[configured_params, {'use_sim_time': use_sim_time}],
            remappings=remappings),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time,
                         'autostart': autostart,
                         'node_names': lifecycle_nodes}]),
    ])
