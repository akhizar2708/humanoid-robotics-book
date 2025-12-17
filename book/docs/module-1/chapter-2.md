---
title: "Python AI Agents with ROS 2"
sidebar_position: 2
---

# Python AI Agents with ROS 2

Modern humanoid robots require AI-powered decision-making to operate autonomously in unstructured environments. This chapter explores how to integrate Python-based AI agents with ROS 2 to create intelligent robotic behaviors.

## Why Python for Robotics AI?

Python has become the dominant language for AI development due to:
- **Rich ecosystem**: PyTorch, TensorFlow, scikit-learn, OpenCV
- **Rapid prototyping**: Quick iteration on algorithms
- **ROS 2 support**: Full-featured Python client library (`rclpy`)
- **Integration**: Easy to call from C++ nodes when performance matters

## Architecture: AI Agent + ROS 2

A typical AI-enabled humanoid robot architecture:

```
┌─────────────────────┐
│   Perception Node   │ → Camera/LIDAR → Image/PointCloud
│   (C++ for speed)   │
└──────────┬──────────┘
           │ Topic: /camera/image_raw
           ▼
┌─────────────────────┐
│   AI Agent Node     │ → Object Detection → Detected Objects
│   (Python + AI)     │    Face Recognition → Person IDs
└──────────┬──────────┘
           │ Topic: /detected_objects
           ▼
┌─────────────────────┐
│  Planning Node      │ → Path Planning → Trajectory
│  (Python/C++)       │    Behavior Tree → Action Sequence
└──────────┬──────────┘
           │ Topic: /cmd_vel
           ▼
┌─────────────────────┐
│  Control Node       │ → Motor Commands → Hardware
│  (C++ real-time)    │
└─────────────────────┘
```

## Building an AI Agent Node

Let's create an object detection node using a pre-trained YOLO model:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D
from cv_bridge import CvBridge
import torch
from ultralytics import YOLO

class ObjectDetectionAgent(Node):
    def __init__(self):
        super().__init__('object_detection_agent')

        # Load YOLO model
        self.model = YOLO('yolov8n.pt')
        self.bridge = CvBridge()

        # Subscribe to camera images
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Publish detected objects
        self.detection_pub = self.create_publisher(
            Detection2DArray,
            '/detected_objects',
            10
        )

        self.get_logger().info('Object detection agent initialized')

    def image_callback(self, msg):
        # Convert ROS Image to OpenCV format
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Run YOLO inference
        results = self.model(cv_image)

        # Convert to ROS Detection2DArray message
        detection_msg = Detection2DArray()
        detection_msg.header = msg.header

        for result in results:
            for box in result.boxes:
                detection = Detection2D()
                detection.bbox.center.x = float((box.xyxy[0][0] + box.xyxy[0][2]) / 2)
                detection.bbox.center.y = float((box.xyxy[0][1] + box.xyxy[0][3]) / 2)
                detection.bbox.size_x = float(box.xyxy[0][2] - box.xyxy[0][0])
                detection.bbox.size_y = float(box.xyxy[0][3] - box.xyxy[0][1])

                # Add class label and confidence
                detection.results[0].id = int(box.cls[0])
                detection.results[0].score = float(box.conf[0])

                detection_msg.detections.append(detection)

        self.detection_pub.publish(detection_msg)
        self.get_logger().info(f'Detected {len(detection_msg.detections)} objects')

def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetectionAgent()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Behavior Trees for Complex Behaviors

For more sophisticated decision-making, use behavior trees. Here's a simple example using `py_trees_ros`:

```python
import py_trees
import py_trees_ros
from rclpy.node import Node

class CheckBatteryLevel(py_trees.behaviour.Behaviour):
    """Check if battery is above threshold."""

    def __init__(self, name, threshold=20.0):
        super().__init__(name)
        self.threshold = threshold
        self.battery_level = 100.0  # Initialize at full

    def update(self):
        if self.battery_level > self.threshold:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

class NavigateToCharger(py_trees.behaviour.Behaviour):
    """Navigate robot to charging station."""

    def update(self):
        # Send navigation goal
        self.logger.info("Navigating to charger...")
        # Implementation would publish to /cmd_vel
        return py_trees.common.Status.RUNNING

# Build behavior tree
root = py_trees.composites.Sequence("MainSequence", memory=True)
root.add_children([
    CheckBatteryLevel("BatteryCheck", threshold=20.0),
    NavigateToCharger("GoToCharger")
])

# Run behavior tree
root.tick_once()
```

## Integrating LLMs for Natural Language Control

Use OpenAI's GPT models to enable natural language robot control:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from openai import OpenAI

class NLPCommandAgent(Node):
    def __init__(self):
        super().__init__('nlp_command_agent')

        self.client = OpenAI()

        # Subscribe to voice commands
        self.subscription = self.create_subscription(
            String,
            '/voice_command',
            self.command_callback,
            10
        )

        # Publish robot actions
        self.action_pub = self.create_publisher(String, '/robot_action', 10)

        self.system_prompt = """You are a humanoid robot control system.
        Convert natural language commands into specific robot actions.
        Output only JSON with keys: action, parameters.

        Available actions:
        - navigate: {x: float, y: float}
        - pick_object: {object_id: string}
        - wave: {hand: "left"|"right"}
        - speak: {text: string}
        """

    def command_callback(self, msg):
        user_command = msg.data

        # Get LLM interpretation
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_command}
            ]
        )

        action_json = response.choices[0].message.content

        # Publish action
        action_msg = String()
        action_msg.data = action_json
        self.action_pub.publish(action_msg)

        self.get_logger().info(f'Command: {user_command} → Action: {action_json}')
```

## Performance Considerations

### When to Use Python vs C++

| Use Python When | Use C++ When |
|-----------------|--------------|
| AI/ML inference (GPU acceleration available) | Real-time control loops (&lt;1ms latency) |
| Rapid prototyping | High-frequency sensor processing |
| Complex logic with many libraries | Memory-constrained embedded systems |
| Behavior trees, planning | Low-level hardware drivers |

### Optimizing Python AI Nodes

```python
# 1. Use async callbacks for non-blocking operations
from rclpy.executors import MultiThreadedExecutor

executor = MultiThreadedExecutor(num_threads=4)
executor.add_node(node)
executor.spin()

# 2. Batch processing for efficiency
def process_batch(self, images):
    # Process multiple images at once
    results = self.model(images, batch=True)
    return results

# 3. GPU acceleration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)
```

## Testing AI Agents

Use ROS 2 bags to record and replay sensor data:

```bash
# Record camera data
ros2 bag record /camera/image_raw

# Replay for testing
ros2 bag play recorded_data

# Run your AI agent
ros2 run my_package object_detection_agent
```

## Key Takeaways

- **Python is ideal** for AI/ML integration with ROS 2
- **Behavior trees** provide structured decision-making for complex behaviors
- **LLMs enable** natural language robot control
- **Choose Python or C++** based on performance requirements
- **Test with ROS bags** for reproducible AI development

:::tip Next Steps
In Chapter 3, we'll explore how to model humanoid robots using URDF, enabling accurate simulation and control.
:::
