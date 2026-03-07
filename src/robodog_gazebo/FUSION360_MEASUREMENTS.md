# Fusion 360 to Gazebo Measurement Guide

This document lists all physical properties you need to extract from your Fusion 360 model to properly configure the Gazebo simulation.

## Component Structure

Your robot leg is broken into these Fusion 360 components:
- **L1A**: First linkage from body (has motor) - acts as part of shoulder
- **L1B**: Second linkage from body (has motor) - acts as part of shoulder  
- **L2**: Tibia/main leg body (no motor)
- **L3**: Paw (no motor)
- **Wheel**: Separate component (not part of L1-L3)

**Mapping to URDF Links:**
- **L1A + L1B** → `hip` link (combined shoulder mechanism)
- **L2** → `tibia` link
- **L3** → `paw` link
- **Wheel** → `wheel` link

**Important:** Since L1A and L1B work together as a shoulder, you have two options:
1. **Combine them**: Measure L1A + L1B together (including both motors) → use for `hip` link
   - Use this if L1A and L1B move together as a single rigid unit
   - Or if they're part of the same joint mechanism
2. **Separate them**: Measure L1A and L1B separately → create two URDF links
   - Use this if L1A and L1B move independently (separate joints)
   - Each would need its own joint in URDF

**Recommendation:** Use Option 1 (combine) for simplicity, unless L1A and L1B move independently. If unsure, check your mechanical design - do L1A and L1B rotate around the same axis or different axes?

---

## How to Get These Values in Fusion 360

1. **Mass Properties**: Select a body → Right-click → `Physical Properties` → Set material → View `Mass Properties`
2. **Center of Mass**: Found in `Mass Properties` dialog (relative to body origin)
3. **Inertia Tensor**: Found in `Mass Properties` dialog → `Inertia` section
4. **Joint Limits**: Measure from your mechanical design (max/min angles)
5. **Material Density**: Set material in Fusion 360, then use calculated mass

### For Components with Motors (L1A, L1B):
- **Include the motor** in your mass property measurements
- Select both the linkage component AND its motor when measuring
- The motor mass, CoM, and inertia will be included in the combined measurement

---

## Table 1: Link Properties (Mass & Inertia)

| Link Name | Mass (kg) | Center of Mass (x, y, z) in meters | Inertia Tensor (kg·m²) |
|-----------|-----------|-----------------------------------|------------------------|
|           |           |                                   |                        |
| **base_link** | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ (usually 0) |
| | | | Ixz: _____ (usually 0) |
| | | | Iyz: _____ (usually 0) |
| | | | |
| **rear_right_hip** (L1A + L1B combined) | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | *Include both L1A and L1B motors* | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **rear_right_tibia** (L2) | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | *No motor* | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **rear_right_paw** (L3) | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | *No motor* | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **rear_right_wheel** | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **rear_left_hip** (L1A + L1B combined) | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | *Include both L1A and L1B motors* | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **rear_left_tibia** | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **rear_left_paw** | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **rear_left_wheel** | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **front_right_hip** (L1A + L1B combined) | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | *Include both L1A and L1B motors* | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **front_right_tibia** (L2) | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | *No motor* | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **front_right_paw** (L3) | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **front_right_wheel** | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **front_left_hip** (L1A + L1B combined) | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | *Include both L1A and L1B motors* | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **front_left_tibia** (L2) | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | *No motor* | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **front_left_paw** (L3) | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |
| | | | |
| **front_left_wheel** | | | |
| | Mass: _____ | COM: (_____, _____, _____) | Ixx: _____ |
| | | | Iyy: _____ |
| | | | Izz: _____ |
| | | | Ixy: _____ |
| | | | Ixz: _____ |
| | | | Iyz: _____ |

---

## Table 2: Joint Properties (Limits & Dynamics)

| Joint Name | Type | Lower Limit (rad) | Upper Limit (rad) | Max Velocity (rad/s) | Max Effort (N·m) | Damping | Friction |
|------------|------|-------------------|-------------------|----------------------|-----------------|---------|----------|
| **rear_right_base_hip_joint** | revolute | _____ | _____ | _____ | _____ | _____ | _____ |
| **rear_right_hip_tibia_joint** | revolute | _____ | _____ | _____ | _____ | _____ | _____ |
| **rear_right_tibia_paw_joint** | revolute | _____ | _____ | _____ | _____ | _____ | _____ |
| **rear_right_paw_wheel_joint** | continuous | N/A | N/A | _____ | _____ | _____ | _____ |
| **rear_left_base_hip_joint** | revolute | _____ | _____ | _____ | _____ | _____ | _____ |
| **rear_left_hip_tibia_joint** | revolute | _____ | _____ | _____ | _____ | _____ | _____ |
| **rear_left_tibia_paw_joint** | revolute | _____ | _____ | _____ | _____ | _____ | _____ |
| **rear_left_paw_wheel_joint** | continuous | N/A | N/A | _____ | _____ | _____ | _____ |
| **front_right_base_hip_joint** | revolute | _____ | _____ | _____ | _____ | _____ | _____ |
| **front_right_hip_tibia_joint** | revolute | _____ | _____ | _____ | _____ | _____ | _____ |
| **front_right_tibia_paw_joint** | revolute | _____ | _____ | _____ | _____ | _____ | _____ |
| **front_right_paw_wheel_joint** | continuous | N/A | N/A | _____ | _____ | _____ | _____ |
| **front_left_base_hip_joint** | revolute | _____ | _____ | _____ | _____ | _____ | _____ |
| **front_left_hip_tibia_joint** | revolute | _____ | _____ | _____ | _____ | _____ | _____ |
| **front_left_tibia_paw_joint** | revolute | _____ | _____ | _____ | _____ | _____ | _____ |
| **front_left_paw_wheel_joint** | continuous | N/A | N/A | _____ | _____ | _____ | _____ |

**Notes:**
- **Lower/Upper Limits**: Maximum rotation angles in radians (π = 3.14159)
- **Max Velocity**: Maximum joint velocity based on motor specs
- **Max Effort**: Maximum torque your motors can provide (N·m)
- **Damping**: Joint damping coefficient (typically 0.01-0.5, higher = more resistance)
- **Friction**: Joint friction coefficient (typically 0.01-0.1)

---

## Table 3: Material Properties (Friction Coefficients)

| Link Name | Material Type | Static Friction (μ1) | Dynamic Friction (μ2) | Notes |
|-----------|---------------|---------------------|----------------------|-------|
| **base_link** | _____ | _____ | _____ | Main body material |
| **rear_right_hip** | _____ | _____ | _____ | |
| **rear_right_tibia** | _____ | _____ | _____ | |
| **rear_right_paw** | _____ | _____ | _____ | |
| **rear_right_wheel** | _____ | _____ | _____ | Higher friction for traction |
| **rear_left_hip** | _____ | _____ | _____ | |
| **rear_left_tibia** | _____ | _____ | _____ | |
| **rear_left_paw** | _____ | _____ | _____ | |
| **rear_left_wheel** | _____ | _____ | _____ | Higher friction for traction |
| **front_right_hip** | _____ | _____ | _____ | |
| **front_right_tibia** | _____ | _____ | _____ | |
| **front_right_paw** | _____ | _____ | _____ | |
| **front_right_wheel** | _____ | _____ | _____ | Higher friction for traction |
| **front_left_hip** | _____ | _____ | _____ | |
| **front_left_tibia** | _____ | _____ | _____ | |
| **front_left_paw** | _____ | _____ | _____ | |
| **front_left_wheel** | _____ | _____ | _____ | Higher friction for traction |

**Typical Friction Values:**
- **Metal on metal**: μ = 0.1-0.3
- **Rubber on concrete**: μ = 0.6-1.0
- **Plastic on metal**: μ = 0.2-0.4
- **Wheels (rubber)**: μ = 0.8-1.2

---

## Table 4: Geometry Dimensions (for Verification)

| Link Name | Geometry Type | Dimensions (meters) | Origin Offset (x, y, z) |
|-----------|---------------|---------------------|------------------------|
| **base_link** | Box 1 | Size: (_____, _____, _____) | (0, 0, 0) |
| | Box 2 | Size: (_____, _____, _____) | (_____, _____, _____) |
| | Box 3 | Size: (_____, _____, _____) | (_____, _____, _____) |
| **rear_right_hip** | Box | Size: (_____, _____, _____) | (_____, _____, _____) |
| **rear_right_tibia** | Box | Size: (_____, _____, _____) | (_____, _____, _____) |
| | Cylinder | Radius: _____, Length: _____ | (_____, _____, _____) |
| **rear_right_paw** | Box | Size: (_____, _____, _____) | (_____, _____, _____) |
| | Sphere | Radius: _____ | (_____, _____, _____) |
| **rear_right_wheel** | Cylinder | Radius: _____, Length: _____ | (0, 0, 0) |
| **rear_left_hip** | Box | Size: (_____, _____, _____) | (_____, _____, _____) |
| **rear_left_tibia** | Box | Size: (_____, _____, _____) | (_____, _____, _____) |
| | Cylinder | Radius: _____, Length: _____ | (_____, _____, _____) |
| **rear_left_paw** | Box | Size: (_____, _____, _____) | (_____, _____, _____) |
| | Sphere | Radius: _____ | (_____, _____, _____) |
| **rear_left_wheel** | Cylinder | Radius: _____, Length: _____ | (0, 0, 0) |
| **front_right_hip** | Box | Size: (_____, _____, _____) | (_____, _____, _____) |
| **front_right_tibia** | Box | Size: (_____, _____, _____) | (_____, _____, _____) |
| | Cylinder | Radius: _____, Length: _____ | (_____, _____, _____) |
| **front_right_paw** | Box | Size: (_____, _____, _____) | (_____, _____, _____) |
| | Sphere | Radius: _____ | (_____, _____, _____) |
| **front_right_wheel** | Cylinder | Radius: _____, Length: _____ | (0, 0, 0) |
| **front_left_hip** | Box | Size: (_____, _____, _____) | (_____, _____, _____) |
| **front_left_tibia** | Box | Size: (_____, _____, _____) | (_____, _____, _____) |
| | Cylinder | Radius: _____, Length: _____ | (_____, _____, _____) |
| **front_left_paw** | Box | Size: (_____, _____, _____) | (_____, _____, _____) |
| | Sphere | Radius: _____ | (_____, _____, _____) |
| **front_left_wheel** | Cylinder | Radius: _____, Length: _____ | (0, 0, 0) |

---

## Table 5: Joint Positions & Orientations

| Joint Name | Parent Link | Child Link | Position (x, y, z) meters | Orientation (roll, pitch, yaw) radians |
|------------|-------------|------------|---------------------------|----------------------------------------|
| **rear_right_base_hip_joint** | base_link | rear_right_hip | (_____, _____, _____) | (_____, _____, _____) |
| **rear_right_hip_tibia_joint** | rear_right_hip | rear_right_tibia | (_____, _____, _____) | (_____, _____, _____) |
| **rear_right_tibia_paw_joint** | rear_right_tibia | rear_right_paw | (_____, _____, _____) | (_____, _____, _____) |
| **rear_right_paw_wheel_joint** | rear_right_paw | rear_right_wheel | (_____, _____, _____) | (_____, _____, _____) |
| **rear_left_base_hip_joint** | base_link | rear_left_hip | (_____, _____, _____) | (_____, _____, _____) |
| **rear_left_hip_tibia_joint** | rear_left_hip | rear_left_tibia | (_____, _____, _____) | (_____, _____, _____) |
| **rear_left_tibia_paw_joint** | rear_left_tibia | rear_left_paw | (_____, _____, _____) | (_____, _____, _____) |
| **rear_left_paw_wheel_joint** | rear_left_paw | rear_left_wheel | (_____, _____, _____) | (_____, _____, _____) |
| **front_right_base_hip_joint** | base_link | front_right_hip | (_____, _____, _____) | (_____, _____, _____) |
| **front_right_hip_tibia_joint** | front_right_hip | front_right_tibia | (_____, _____, _____) | (_____, _____, _____) |
| **front_right_tibia_paw_joint** | front_right_tibia | front_right_paw | (_____, _____, _____) | (_____, _____, _____) |
| **front_right_paw_wheel_joint** | front_right_paw | front_right_wheel | (_____, _____, _____) | (_____, _____, _____) |
| **front_left_base_hip_joint** | base_link | front_left_hip | (_____, _____, _____) | (_____, _____, _____) |
| **front_left_hip_tibia_joint** | front_left_hip | front_left_tibia | (_____, _____, _____) | (_____, _____, _____) |
| **front_left_tibia_paw_joint** | front_left_tibia | front_left_paw | (_____, _____, _____) | (_____, _____, _____) |
| **front_left_paw_wheel_joint** | front_left_paw | front_left_wheel | (_____, _____, _____) | (_____, _____, _____) |

---

## Quick Reference: Fusion 360 Steps

### Getting Mass Properties:

#### For Single Components (L2, L3, Wheel):
1. Select the body/component
2. Right-click → `Physical Properties`
3. Set material (if not already set)
4. Click `Calculate` or `Update`
5. View `Mass Properties` tab:
   - **Mass**: Total mass in kg
   - **Center of Mass**: X, Y, Z coordinates relative to body origin
   - **Inertia**: Click `Inertia` button to see full tensor matrix

#### For Combined Components (L1A + L1B for hip link):
1. Select **both** L1A and L1B components (including their motors)
   - Hold Ctrl/Cmd and click both components
   - Or select the parent assembly containing both
2. Right-click → `Physical Properties`
3. Ensure materials are set for all parts
4. Click `Calculate` or `Update`
5. View `Mass Properties` tab:
   - **Mass**: Combined mass of L1A + L1B + both motors
   - **Center of Mass**: Combined CoM of all selected components
   - **Inertia**: Combined inertia tensor of all selected components
6. **Important**: Make sure the coordinate system/origin matches your URDF link frame

### Getting Joint Limits:
1. Measure maximum rotation angles from your mechanical design
2. Convert degrees to radians: `radians = degrees × π / 180`
3. Consider mechanical stops and motor capabilities

### Getting Motor Specifications:
- **Max Velocity**: From motor datasheet (RPM → rad/s: `rad/s = RPM × 2π / 60`)
- **Max Effort**: From motor datasheet (torque in N·m)
- **Damping**: Estimate based on gearbox/motor type (0.01-0.5 typical)

---

## Important Notes

1. **Units**: All measurements must be in **meters** and **kilograms**
2. **Inertia Tensor**: Fusion 360 may give inertia about center of mass or origin - verify which one
3. **Symmetry**: If parts are symmetric (left/right), you can copy values
4. **Material Density**: Set realistic materials in Fusion 360 for accurate mass calculations
5. **Joint Origins**: Measure joint positions relative to parent link's origin frame

---

## Current Values (for reference - replace with your measurements)

See `urdf/robodog_skeleton.urdf` for current placeholder values that need to be replaced.
