#!/usr/bin/env python3

import os
import subprocess
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

# Enable colored output
os.environ["RCUTILS_COLORIZED_OUTPUT"] = "1"


def launch_setup(context, *args, **kwargs):
    # Get launch configuration values
    urdf_file = LaunchConfiguration('urdf_file').perform(context)
    rviz_config = LaunchConfiguration('rviz_config').perform(context)
    
    # Process URDF file through xacro to expand variables
    try:
        result = subprocess.run(
            ['xacro', urdf_file],
            capture_output=True,
            text=True,
            check=True
        )
        robot_description_content = result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to process URDF with xacro: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("xacro command not found. Please install xacro package.")
    
    robot_description = {'robot_description': robot_description_content}
    
    nodes = []
    
    # Robot State Publisher node
    nodes.append(Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    ))
    
    # Joint State Publisher GUI node (for interactive joint control)
    nodes.append(Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
        condition=IfCondition(LaunchConfiguration('use_gui'))
    ))
    
    # Joint State Publisher node (non-GUI fallback)
    nodes.append(Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        condition=UnlessCondition(LaunchConfiguration('use_gui'))
    ))
    
    # RViz2 node - only add config if file exists
    rviz_args = []
    if rviz_config and os.path.exists(rviz_config):
        rviz_args = ['-d', rviz_config]
    
    nodes.append(Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=rviz_args,
        condition=IfCondition(LaunchConfiguration('use_rviz'))
    ))
    
    return nodes


def generate_launch_description():
    # Get the package share directory
    package_name = 'robodog_gazebo'
    
    # Path to the URDF file
    default_urdf_path = os.path.join(
        get_package_share_directory(package_name),
        'urdf',
        'robodog_skeleton.urdf'
    )
    
    # Path to RViz config file (optional)
    default_rviz_config_path = os.path.join(
        get_package_share_directory(package_name),
        'rviz2',
        'view_robot.rviz'
    )
    
    # Launch arguments
    urdf_file_arg = DeclareLaunchArgument(
        'urdf_file',
        default_value=default_urdf_path,
        description='Path to the URDF file'
    )
    
    use_gui_arg = DeclareLaunchArgument(
        'use_gui',
        default_value='true',
        description='Flag to enable joint_state_publisher_gui'
    )
    
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=default_rviz_config_path,
        description='Path to RViz config file (optional)'
    )
    
    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Flag to enable RViz'
    )
    
    return LaunchDescription([
        urdf_file_arg,
        use_gui_arg,
        rviz_config_arg,
        use_rviz_arg,
        OpaqueFunction(function=launch_setup),
    ])

