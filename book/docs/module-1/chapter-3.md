---
title: "Humanoid Modeling with URDF"
sidebar_position: 3
---

# Humanoid Modeling with URDF

URDF (Unified Robot Description Format) is an XML-based format for describing robot kinematics, dynamics, and visual properties. For humanoid robots, accurate URDF models are essential for simulation, visualization, and control.

## Why URDF for Humanoid Robots?

A humanoid robot typically has:
- **30-50 degrees of freedom** (DOF): joints in legs, arms, torso, head
- **Complex kinematic chains**: serial and parallel linkages
- **Dynamic properties**: mass, inertia, friction for physics simulation
- **Collision geometry**: for motion planning and safety

URDF provides a standard way to describe all these properties, enabling:
- **Simulation** in Gazebo or MuJoCo
- **Visualization** in RViz
- **Motion planning** with MoveIt 2
- **Control** using standard ROS 2 controllers

## URDF Structure

A URDF file defines:
- **Links**: Rigid bodies (torso, thigh, shin, etc.)
- **Joints**: Connections between links (revolute, prismatic, fixed)
- **Visual elements**: 3D meshes for rendering
- **Collision elements**: Simplified geometry for collision detection
- **Inertial properties**: Mass, center of mass, inertia tensor

## Example: Humanoid Arm

Let's model a simple humanoid arm with shoulder and elbow joints:

```xml
<?xml version="1.0"?>
<robot name="humanoid_arm">

  <!-- Base link (torso attachment point) -->
  <link name="shoulder_base">
    <visual>
      <geometry>
        <box size="0.1 0.1 0.1"/>
      </geometry>
      <material name="grey">
        <color rgba="0.5 0.5 0.5 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.1 0.1 0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0"
               iyy="0.001" iyz="0.0" izz="0.001"/>
    </inertial>
  </link>

  <!-- Upper arm link -->
  <link name="upper_arm">
    <visual>
      <geometry>
        <cylinder length="0.3" radius="0.04"/>
      </geometry>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <material name="blue">
        <color rgba="0.0 0.0 1.0 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.3" radius="0.04"/>
      </geometry>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <origin xyz="0 0 -0.15"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0"
               iyy="0.01" iyz="0.0" izz="0.001"/>
    </inertial>
  </link>

  <!-- Shoulder joint (revolute) -->
  <joint name="shoulder_joint" type="revolute">
    <parent link="shoulder_base"/>
    <child link="upper_arm"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>  <!-- Rotation around Y-axis -->
    <limit lower="-1.57" upper="3.14" effort="100" velocity="2.0"/>
    <dynamics damping="0.5" friction="0.1"/>
  </joint>

  <!-- Forearm link -->
  <link name="forearm">
    <visual>
      <geometry>
        <cylinder length="0.25" radius="0.03"/>
      </geometry>
      <origin xyz="0 0 -0.125" rpy="0 0 0"/>
      <material name="blue">
        <color rgba="0.0 0.0 1.0 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.25" radius="0.03"/>
      </geometry>
      <origin xyz="0 0 -0.125" rpy="0 0 0"/>
    </collision>
    <inertial>
      <mass value="0.7"/>
      <origin xyz="0 0 -0.125"/>
      <inertia ixx="0.005" ixy="0.0" ixz="0.0"
               iyy="0.005" iyz="0.0" izz="0.0005"/>
    </inertial>
  </link>

  <!-- Elbow joint (revolute) -->
  <joint name="elbow_joint" type="revolute">
    <parent link="upper_arm"/>
    <child link="forearm"/>
    <origin xyz="0 0 -0.3" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="0" upper="2.35" effort="50" velocity="2.0"/>
    <dynamics damping="0.3" friction="0.05"/>
  </joint>

</robot>
```

## Loading URDF in ROS 2

### Method 1: robot_state_publisher

The standard way to load a URDF in ROS 2:

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    urdf_file = os.path.join(
        get_package_share_directory('my_humanoid'),
        'urdf',
        'humanoid.urdf'
    )

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': True
            }]
        )
    ])
```

### Method 2: Xacro for Parameterized Models

For complex humanoid models, use Xacro to avoid repetition:

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid">

  <!-- Macro for creating a leg -->
  <xacro:macro name="leg" params="side reflect">

    <link name="${side}_thigh">
      <visual>
        <geometry>
          <cylinder length="0.4" radius="0.06"/>
        </geometry>
        <material name="grey"/>
      </visual>
      <inertial>
        <mass value="2.0"/>
        <inertia ixx="0.02" ixy="0" ixz="0"
                 iyy="0.02" iyz="0" izz="0.002"/>
      </inertial>
    </link>

    <joint name="${side}_hip_joint" type="revolute">
      <parent link="pelvis"/>
      <child link="${side}_thigh"/>
      <origin xyz="0 ${0.15 * reflect} 0" rpy="0 0 0"/>
      <axis xyz="0 1 0"/>
      <limit lower="-1.57" upper="1.57" effort="200" velocity="2.0"/>
    </joint>

    <link name="${side}_shin">
      <visual>
        <geometry>
          <cylinder length="0.35" radius="0.05"/>
        </geometry>
        <material name="grey"/>
      </visual>
      <inertial>
        <mass value="1.5"/>
        <inertia ixx="0.015" ixy="0" ixz="0"
                 iyy="0.015" iyz="0" izz="0.0015"/>
      </inertial>
    </link>

    <joint name="${side}_knee_joint" type="revolute">
      <parent link="${side}_thigh"/>
      <child link="${side}_shin"/>
      <origin xyz="0 0 -0.4" rpy="0 0 0"/>
      <axis xyz="0 1 0"/>
      <limit lower="0" upper="2.35" effort="150" velocity="2.0"/>
    </joint>

  </xacro:macro>

  <!-- Use macro to create both legs -->
  <xacro:leg side="left" reflect="1"/>
  <xacro:leg side="right" reflect="-1"/>

</robot>
```

## Visualizing in RViz

Launch RViz to see your humanoid model:

```bash
# Terminal 1: Launch robot state publisher
ros2 launch my_humanoid_description display.launch.py

# Terminal 2: Publish joint states
ros2 run joint_state_publisher_gui joint_state_publisher_gui
```

In RViz:
1. Add **RobotModel** display
2. Set **Robot Description** topic to `/robot_description`
3. Add **TF** display to see coordinate frames

## Simulation in Gazebo

To simulate physics in Gazebo, add transmission and plugin tags:

```xml
<transmission name="shoulder_transmission">
  <type>transmission_interface/SimpleTransmission</type>
  <joint name="shoulder_joint">
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
  </joint>
  <actuator name="shoulder_motor">
    <mechanicalReduction>1</mechanicalReduction>
  </actuator>
</transmission>

<gazebo>
  <plugin name="gazebo_ros_control" filename="libgazebo_ros_control.so">
    <robotNamespace>/humanoid</robotNamespace>
  </plugin>
</gazebo>
```

## Calculating Inertial Properties

For accurate simulation, compute inertia tensors:

```python
import numpy as np

def cylinder_inertia(mass, radius, length):
    """Calculate inertia tensor for a cylinder."""
    ixx = (1/12) * mass * (3 * radius**2 + length**2)
    iyy = ixx
    izz = (1/2) * mass * radius**2
    return ixx, iyy, izz

# Example: 1kg cylinder, 0.04m radius, 0.3m length
ixx, iyy, izz = cylinder_inertia(1.0, 0.04, 0.3)
print(f"ixx={ixx:.6f}, iyy={iyy:.6f}, izz={izz:.6f}")
```

## Best Practices

1. **Use meaningful names**: `left_shoulder_joint` not `joint_23`
2. **Set realistic limits**: Joint limits based on human range of motion
3. **Accurate inertias**: Use CAD software or formulas for primitive shapes
4. **Collision simplification**: Use boxes/cylinders for collision, detailed meshes for visuals
5. **Test incrementally**: Build one limb at a time, test before adding more

## Common Pitfalls

- **Missing inertial tags**: Gazebo will use default values (often wrong)
- **Zero mass**: Physics will fail
- **Incorrect joint axes**: Robot will bend the wrong way
- **Overlapping collision geometry**: Causes physics instabilities

## Key Takeaways

- **URDF describes** robot kinematics, dynamics, and visual properties
- **Links are rigid bodies**, joints connect them
- **Xacro enables** parameterized, reusable models
- **Accurate inertias** are crucial for realistic simulation
- **Test in RViz** before moving to Gazebo

:::tip Further Reading
- [URDF Tutorial](http://wiki.ros.org/urdf/Tutorials)
- [Xacro Documentation](http://wiki.ros.org/xacro)
- [Gazebo URDF Extensions](http://gazebosim.org/tutorials?tut=ros_urdf)
:::
