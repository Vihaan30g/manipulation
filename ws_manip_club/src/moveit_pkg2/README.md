# MoveIt2 Pose Goal Planning Failure Reproduction

## Environment

* Ubuntu 22.04
* ROS 2 Humble
* MoveIt2
* Ignition Fortress


## Installation

Install dependencies:

```bash
rosdep install --from-paths src --ignore-src -r -y
```

## Launch

Terminal 1:

```bash
ros2 launch moveit_pkg2 ignition_sim.launch.py
```

Terminal 2:

```bash
ros2 launch moveit_pkg2 moveit.launch.py
```

## Reproduction Script

The script used to send the pose goal is:

```text
src/direct_move.py
```

