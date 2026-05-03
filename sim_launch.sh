#!/bin/bash

# Main launch script for urdf_color simulation with SLAM and Teleop
# Usage: ./sim_launch.sh

SESSION="urdf_sim"

# Kill existing session and processes to ensure a clean clock and environment
tmux kill-session -t $SESSION 2>/dev/null
pkill -9 -f ros2
pkill -9 -f gz
pkill -9 -f rtabmap
pkill -9 -f rviz2
sleep 2

# Ensure we are in the workspace root
if [ ! -d "install" ]; then
    echo "Error: 'install' directory not found. Please run this script from the workspace root."
    exit 1
fi

# Create a new tmux session, detached
tmux new-session -d -s $SESSION

# Window 0: Gazebo
tmux rename-window -t $SESSION:0 'Gazebo'
tmux send-keys -t $SESSION:0 "source /opt/ros/jazzy/setup.bash && source install/setup.bash" C-m
tmux send-keys -t $SESSION:0 "ros2 launch urdf_color gazebo.launch.py" C-m

# Wait for Gazebo to start (clock topic is a good indicator)
echo "Waiting for Gazebo clock..."
until ros2 topic echo /clock --once > /dev/null 2>&1; do sleep 1; done
echo "Clock detected!"

# Window 3: Motor Command (Bridge cmd_vel to leg joints)
tmux new-window -t $SESSION:3 -n 'MotorCmd'
tmux send-keys -t $SESSION:3 "source /opt/ros/jazzy/setup.bash && source install/setup.bash" C-m
tmux send-keys -t $SESSION:3 "python3 src/urdf_color/scripts/motor_command.py" C-m

sleep 15

# Window 1: SLAM (RTAB-Map)
# This provides the costmap/map you were missing
tmux new-window -t $SESSION:1 -n 'SLAM'
tmux send-keys -t $SESSION:1 "source /opt/ros/jazzy/setup.bash && source install/setup.bash" C-m
tmux send-keys -t $SESSION:1 "ros2 launch rtabmap_launch rtabmap.launch.py rtabmap_args:=\"--delete_db_on_start --Grid/FromDepth true --Grid/RangeMax 5\" rgb_topic:=/zed/zed_node/rgb/image_rect_color depth_topic:=/zed/zed_node/depth/depth_registered camera_info_topic:=/zed/zed_node/rgb/image_rect_color/camera_info frame_id:=base_footprint odom_topic:=/zed/zed_node/odom visual_odometry:=false approx_sync:=true use_sim_time:=true" C-m

# Window 2: RVizp
tmux new-window -t $SESSION:2 -n 'RViz'
tmux send-keys -t $SESSION:2 "source /opt/ros/jazzy/setup.bash && source install/setup.bash" C-m
tmux send-keys -t $SESSION:2 "rviz2 -d src/urdf_color/config/display.rviz --ros-args -p use_sim_time:=true" C-m

# Window 4: Teleop
tmux new-window -t $SESSION:4 -n 'Teleop'
tmux send-keys -t $SESSION:4 "source /opt/ros/jazzy/setup.bash && source install/setup.bash" C-m
tmux send-keys -t $SESSION:4 "ros2 run teleop_twist_keyboard teleop_twist_keyboard" C-m

# Window 5: Nav2
tmux new-window -t $SESSION:5 -n 'Nav2'
tmux send-keys -t $SESSION:5 "source /opt/ros/jazzy/setup.bash && source install/setup.bash" C-m
tmux send-keys -t $SESSION:5 "ros2 launch urdf_color navigation.launch.py use_sim_time:=true" C-m

# Select the Teleop window so the user can start driving immediately
tmux select-window -t $SESSION:4

# Attach to the session
tmux attach-session -t $SESSION
