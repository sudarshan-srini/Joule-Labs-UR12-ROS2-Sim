# UR12e Autonomous Motion Control Architecture

This repository contains a ROS 2 Jazzy system architecture designed for autonomous Cartesian motion control of a Universal Robots UR12e using `MoveItPy` and Gazebo simulation. The pipeline bypasses the standard MoveIt execution manager to resolve clock synchronization conflicts in simulation, sending trajectory goals directly to the joint controllers via a native Action Client.

## System Prerequisites
* **OS:** Ubuntu 24.04 (Noble Numbat)
* **ROS 2:** Jazzy Jalisco
* **Build Tools:** `colcon`, `rosdep`

## Workspace Initialization & Build Instructions

To deploy this architecture on a new machine, follow these exact steps to clone the source packages, install system dependencies, and compile the workspace.

### 1. Initialize Workspace & Clone Repositories
Create a new ROS 2 workspace, navigate to the source directory, and clone this repository along with the official Universal Robots Jazzy branches:

```bash
mkdir -p ~/ur12e_ws/src
cd ~/ur12e_ws/src

# Clone this system architecture (replace with actual URL)
git clone [https://github.com/joulelabs/ur12e-autonomous-controller.git](https://github.com/joulelabs/ur12e-autonomous-controller.git) .

# Clone required UR simulation and description packages
git clone -b jazzy [https://github.com/UniversalRobots/Universal_Robots_ROS2_Description.git](https://github.com/UniversalRobots/Universal_Robots_ROS2_Description.git)
git clone -b jazzy [https://github.com/UniversalRobots/Universal_Robots_ROS2_GZ_Simulation.git](https://github.com/UniversalRobots/Universal_Robots_ROS2_GZ_Simulation.git)
