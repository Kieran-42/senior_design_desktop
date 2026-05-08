#!/bin/bash

# Main launch script for urdf_color simulation with SLAM and Teleop
# Usage:
#   ./sim_launch.sh
#   ./sim_launch.sh <world_path> [world_name] [gz_resource_path]

SESSION="urdf_sim"
WORLD_PATH="$1"
WORLD_NAME="$2"
GZ_RESOURCE_PATH_ARG="$3"
PATCHED_WORLD_PATH=""

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

WORKSPACE_ROOT="$(pwd)"
DEFAULT_GZ_RESOURCE_PATH="$WORKSPACE_ROOT/install/urdf_color/share"

if [ -n "$WORLD_PATH" ]; then
    if [ ! -f "$WORLD_PATH" ]; then
        echo "Error: world file not found: $WORLD_PATH"
        exit 1
    fi

    WORLD_PATH="$(readlink -f "$WORLD_PATH")"
    WORLD_RESOURCE_DIR="$(dirname "$WORLD_PATH")"
    WORLD_PACKAGE_DIR="$(dirname "$WORLD_RESOURCE_DIR")"
    WORLD_MODELS_DIR="$WORLD_PACKAGE_DIR/models"
    DETECTED_WORLD_NAME="$(sed -n "s/.*<world[[:space:]][^>]*name=['\"]\([^'\"]*\)['\"].*/\1/p" "$WORLD_PATH" | head -n 1)"
    if ! grep -q "gz-sim-sensors-system" "$WORLD_PATH"; then
        PATCHED_WORLD_PATH="/tmp/urdf_color_$(basename "$WORLD_PATH").$$"
        awk '
            {
                print
                if (!inserted && $0 ~ /<world[[:space:]>]/) {
                    print "    <plugin filename=\"gz-sim-physics-system\" name=\"gz::sim::systems::Physics\"/>"
                    print "    <plugin filename=\"gz-sim-user-commands-system\" name=\"gz::sim::systems::UserCommands\"/>"
                    print "    <plugin filename=\"gz-sim-scene-broadcaster-system\" name=\"gz::sim::systems::SceneBroadcaster\"/>"
                    print "    <plugin filename=\"gz-sim-contact-system\" name=\"gz::sim::systems::Contact\"/>"
                    print "    <plugin filename=\"gz-sim-sensors-system\" name=\"gz::sim::systems::Sensors\">"
                    print "      <render_engine>ogre2</render_engine>"
                    print "    </plugin>"
                    print "    <plugin filename=\"gz-sim-imu-system\" name=\"gz::sim::systems::Imu\"/>"
                    inserted = 1
                }
            }
        ' "$WORLD_PATH" > "$PATCHED_WORLD_PATH"
        WORLD_PATH="$PATCHED_WORLD_PATH"
    fi

    WORLD_NAME="${WORLD_NAME:-${DETECTED_WORLD_NAME:-default}}"
    if [ -z "$GZ_RESOURCE_PATH_ARG" ]; then
        GZ_RESOURCE_PATH_ARG="$WORLD_RESOURCE_DIR"
        if [ -d "$WORLD_MODELS_DIR" ]; then
            GZ_RESOURCE_PATH_ARG="$GZ_RESOURCE_PATH_ARG:$WORLD_MODELS_DIR"
        fi
    fi
    GZ_RESOURCE_PATH_ARG="$DEFAULT_GZ_RESOURCE_PATH:$GZ_RESOURCE_PATH_ARG"
    GAZEBO_LAUNCH_CMD="ros2 launch urdf_color gazebo.launch.py world:=$WORLD_PATH world_name:=$WORLD_NAME gz_resource_path:=$GZ_RESOURCE_PATH_ARG"
else
    WORLD_NAME="${WORLD_NAME:-robodog_world}"
    GAZEBO_LAUNCH_CMD="ros2 launch urdf_color gazebo.launch.py world_name:=$WORLD_NAME"
fi

# Create a new tmux session, detached
tmux new-session -d -s $SESSION

# Window 0: Gazebo
tmux rename-window -t $SESSION:0 'Gazebo'
tmux send-keys -t $SESSION:0 "source /opt/ros/jazzy/setup.bash && source install/setup.bash" C-m
tmux send-keys -t $SESSION:0 "$GAZEBO_LAUNCH_CMD" C-m

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
