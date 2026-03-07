# Robodog Gazebo Package

This ROS2 package contains the URDF description for the robodog robot and provides launch files to visualize it in RViz2 or simulate it in Gazebo.

## Package Structure

```
robodog_gazebo/
├── CMakeLists.txt
├── package.xml
├── README.md
├── config/
│   └── robodog_controllers.yaml
├── launch/
│   ├── display.launch.py
│   └── robot_launch.py
├── urdf/
│   └── robodog_skeleton.urdf
└── rviz2/
    └── view_robot.rviz (optional)
```

## Building the Package

From your ROS2 workspace root:

```bash
cd ~/ros_ws
colcon build --packages-select robodog_gazebo
source install/setup.bash
```

**Important:** Use the package name **robodog_gazebo** (not `robodog_description`). If you see errors about `robodog_description` or missing `description/robodog.urdf.xacro`, you are either launching the wrong package or have a stale install. Clean and rebuild:

```bash
cd ~/ros_ws
rm -rf build/robodog_description install/robodog_description build/robodog_gazebo install/robodog_gazebo
colcon build --packages-select robodog_gazebo
source install/setup.bash
```

## Usage

### Launch Gazebo simulation (spawn robot in Gazebo)

```bash
ros2 launch robodog_gazebo robot_launch.py
```

### Launch RViz visualization (no Gazebo)

To launch the robot model with RViz2 and joint state publisher GUI:

```bash
ros2 launch robodog_gazebo display.launch.py
```

### Display launch options

- `urdf_file`: Path to the URDF file (default: package's `urdf/robodog_skeleton.urdf`)
- `use_gui`: Enable joint_state_publisher_gui (default: `true`)
- `use_rviz`: Enable RViz2 (default: `true`)
- `rviz_config`: Path to RViz config file (default: package's config)

Example:

```bash
ros2 launch robodog_gazebo display.launch.py use_gui:=false use_rviz:=true
```

### Without RViz (for headless systems)

```bash
ros2 launch robodog_gazebo display.launch.py use_rviz:=false
```

### Without GUI (using non-GUI joint state publisher)

```bash
ros2 launch robodog_gazebo display.launch.py use_gui:=false
```

## What the Launch Files Do

- **robot_launch.py**: Starts Gazebo, loads the xacro URDF, runs robot_state_publisher, and spawns the robot in Gazebo.
- **display.launch.py**: Runs robot_state_publisher, joint_state_publisher (GUI or not), and optionally RViz2 (no Gazebo).

## Dependencies

- `robot_state_publisher`, `joint_state_publisher`, `joint_state_publisher_gui`
- `rviz2`, `xacro`
- `gazebo_ros`, `gazebo_ros2_control`, `gazebo_plugins`
- `controller_manager`, `joint_state_broadcaster`, `position_controllers`, `velocity_controllers`
