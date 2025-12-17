---
title: "ROS 2 Fundamentals for Physical AI"
sidebar_position: 1
---

# ROS 2 Fundamentals for Physical AI

ROS 2 (Robot Operating System 2) is a middleware framework that provides the communication infrastructure for building distributed robotic systems. Unlike traditional monolithic robot software, ROS 2 enables you to build modular, scalable applications where different components communicate through well-defined interfaces.

## Why ROS 2 for Humanoid Robotics?

Humanoid robots are inherently complex systems that require coordinating multiple subsystems:
- **Perception**: Cameras, LIDAR, depth sensors
- **Locomotion**: Motors, actuators, balance control
- **Manipulation**: Arm control, grasping, object interaction
- **Cognition**: AI models, decision-making, planning

ROS 2 provides the middleware layer that allows these subsystems to communicate reliably and efficiently.

## Core Concepts

### Nodes

A **node** is an independent process that performs a specific function. In a humanoid robot, you might have:
- A camera node that publishes image data
- A face detection node that subscribes to images and publishes detected faces
- A motor control node that receives movement commands

```python
import rclpy
from rclpy.node import Node

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)

    def publish_message(self):
        msg = String()
        msg.data = 'Hello from ROS 2!'
        self.publisher_.publish(msg)
```

### Topics (Publish-Subscribe)

Topics enable asynchronous, many-to-many communication. Multiple nodes can publish to the same topic, and multiple nodes can subscribe.

**Use case**: A camera node publishes images to a `/camera/image_raw` topic. Multiple nodes (object detection, face recognition, motion tracking) can all subscribe to process the images independently.

### Services (Request-Response)

Services provide synchronous request-response communication. A client node sends a request and waits for the response.

**Use case**: A planning node requests the current joint positions from a robot state service before computing a new trajectory.

```python
from std_srvs.srv import SetBool

def set_mode_callback(request, response):
    if request.data:
        # Enable autonomous mode
        response.success = True
        response.message = "Autonomous mode enabled"
    else:
        response.success = False
        response.message = "Manual mode enabled"
    return response
```

### Actions (Long-Running Tasks)

Actions support long-running tasks with feedback and the ability to cancel.

**Use case**: A "walk to position" action that provides feedback on progress and can be canceled if an obstacle is detected.

## ROS 2 vs ROS 1

| Feature | ROS 1 | ROS 2 |
|---------|-------|-------|
| **Communication** | Custom TCP/UDP | DDS (Data Distribution Service) |
| **Real-time Support** | Limited | Built-in with DDS QoS |
| **Security** | Basic | DDS Security (authentication, encryption) |
| **Multi-robot** | Difficult | Native support |
| **Platform Support** | Linux-focused | Linux, Windows, macOS |

## DDS Middleware

ROS 2 uses DDS (Data Distribution Service) as its middleware layer. DDS provides:
- **Quality of Service (QoS)**: Configure reliability, durability, latency
- **Discovery**: Automatic node and topic discovery
- **Security**: Built-in authentication and encryption

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

# Configure QoS for sensor data (best effort, volatile)
sensor_qos = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    depth=10
)

# Configure QoS for commands (reliable, transient local)
command_qos = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
    depth=10
)
```

## Hands-On: Your First ROS 2 Node

Let's create a simple humanoid robot state publisher:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class HumanoidStatePublisher(Node):
    def __init__(self):
        super().__init__('humanoid_state_publisher')
        self.publisher_ = self.create_publisher(
            JointState,
            'joint_states',
            10
        )
        self.timer = self.create_timer(0.1, self.publish_state)
        self.get_logger().info('Humanoid state publisher started')

    def publish_state(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow']
        msg.position = [0.0, 0.0, 1.57, 1.57]  # Example joint positions
        msg.velocity = [0.0, 0.0, 0.0, 0.0]
        msg.effort = [0.0, 0.0, 0.0, 0.0]

        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = HumanoidStatePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Run the node:

```bash
python3 humanoid_state_publisher.py
```

## Next Steps

Now that you understand ROS 2 fundamentals, we'll explore:
- **Chapter 2**: Integrating Python AI agents with ROS 2
- **Chapter 3**: Modeling humanoid robots with URDF
- **Chapter 4**: Building a complete perception pipeline

## Key Takeaways

- ROS 2 is a **middleware framework**, not a programming language or operating system
- **Nodes** are independent processes that communicate via **topics**, **services**, and **actions**
- **DDS** provides the underlying communication layer with built-in QoS and security
- ROS 2 is designed for **real-time, distributed, multi-robot systems**

:::tip Further Reading
- [ROS 2 Official Documentation](https://docs.ros.org/en/rolling/)
- [ROS 2 Design Principles](https://design.ros2.org/)
- [DDS Specification](https://www.omg.org/spec/DDS/)
:::
