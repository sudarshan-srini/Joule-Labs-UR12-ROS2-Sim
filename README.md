# UR12e ROS2 Simulation Architecture

This repository contains a ROS 2 Jazzy system architecture designed for autonomous Cartesian motion control of a Universal Robots UR12e using `MoveItPy` and Gazebo simulation. The pipeline bypasses the standard MoveIt execution manager to resolve clock synchronization conflicts in simulation, sending trajectory goals directly to the joint controllers via a native Action Client.

## System Prerequisites
* **OS:** Ubuntu 24.04 (Noble Numbat)
* **ROS 2:** Jazzy Jalisco
* **Physics Emulator**: Gazebo Harmonic
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
```
### 2.  Resolve System Dependencies
Use rosdep to automatically scan the package configuration files and pull down all missing C++ binaries, Python modules (e.g., scipy), and core ROS 2 libraries required by the architecture:

```bash
cd ~/ur12e_ws
rosdep update
rosdep install --from-paths src --ignore-src -y
```

### 3. Compile the Architecture (The Build Step)
You must compile the workspace to generate the necessary build/ and install/ directories. Navigate to the root of your workspace and choose one of the following build methods:

**Option A: Standard Deployment**:

If you only intend to run the simulation without modifying the underlying code, a standard build is sufficient:

```bash
cd ~/ur12e_ws
colcon build
```
**Option B: Active Deployment**:

If you plan to modify the Python nodes, compile with the symlink flag. This creates a dynamic link between the source code and the compiled installation, allowing live edits to take effect immediately without requiring a full system rebuild.

```bash
cd ~/ur12e_ws
colcon build --symlink-install
```

### 4. Execution

Ensure the compiled environment is sourced in every fresh terminal before initializing nodes:

```bash
cd ~/ur12e_ws
. install/setup.bash
```

**Terminal 1: Simulation Hardware Interface**

Initializes the physical simulation environment in Gazebo, spawns the UR12e, and loads the joint trajectory hardware controllers.

```bash
source ~/ur12e_ws/install/setup.bash
ros2 launch ur_simulation_gz ur_sim_control.launch.py ur_type:=ur12e
```

**Terminal 2: Motion Planning Engine & Visualization**

Deploys the MoveIt 2 core math engine, loads the OMPL planning configurations, establishes the robot semantic structures, and opens the RViz visualizer synced to simulation time.

```bash
source ~/ur12e_ws/install/setup.bash
ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur12e use_sim_time:=true launch_rviz:=true
```

**Terminal 3: Vision Controller Node - Currently Set To Specific Coordinates**

Executes the vision_controller package given a set of cartesian coordinates. Verifies the Inverse Kinematics before triggering the hardware execution.
Robot spawns at default configuration. Run script to move to our custom home position.

The accepted argument is a position & rotation vector. You can override the position of the robot by editing the first three parameters of the list, and the orientation / rotation of the end-effector by editing the last three parameters of the list:

[x,y,z,Rx,Ry,Rz] -- can be read from the teaching pendant interface

```bash
source ~/ur12e_ws/install/setup.bash
ros2 run vision_control_pkg motion_controller
```

