# ROS 2 Autonomous 2 Wheels Mobile Robot Simulation

This repository contains the complete ROS 2 Humble and Gazebo (Ignition) simulation for an autonomous differential-drive mobile robot. The project demonstrates multi-waypoint navigation, dynamic obstacle avoidance in branching corridors, and a custom Boustrophedon (zigzag) coverage algorithm.

## Robot Specifications

* **Drive System:** Differential Drive (Gazebo plugin)

* **Sensors:**

  * 360° 2D LiDAR (`/scan`)

  * 4x Short-Range Ultrasonic Sensors (`/ultrasonic/front_left`, etc.)

  * RGB-D Depth Camera

  * 9-Axis BNO055 IMU

* **Framework:** ROS 2 Humble, Navigation2 (Nav2), xacro, ros_gz_bridge

## Prerequisites & Build Instructions

Ensure you have ROS 2 Humble and Ignition Gazebo installed on your system.

1. **Clone the repository:**

   ```
   mkdir -p ~/hrl_ws/src
   cd ~/hrl_ws/src
   git clone <your-repository-url> .
   
   ```

2. **Build the workspace:**

   ```
   cd ~/hrl_ws
   colcon build
   
   ```

3. **Source the workspace:**

   ```
   source install/setup.bash
   
   ```

## Execution & Tasks

### Task A: Multi-Waypoint Navigation

The robot autonomously navigates through a predefined sequence of topological waypoints (A → B → C → Home) using the Nav2 stack, actively avoiding obstacles using its onboard LiDAR and ultrasonic sensors.


*(Replace `images/task_a.png` with your screenshot or GIF)*

**Execution:**

1. Launch the simulation:

   ```
   ros2 launch bot_simulation sim_bringup.launch.py
   
   ```

2. Launch the Nav2 stack (ensure strict lowercase `true`):

   ```
   ros2 launch nav2_bringup bringup_launch.py use_sim_time:=true map:=src/bot_navigation/maps/corridor_map.yaml
   
   ```

3. Open RViz2, set the **2D Pose Estimate**, and use the **Nav Through Poses** tool to assign the waypoint sequence.

### Task B: Branching Corridor Navigation

The robot dynamically plans paths through branching geometric environments, exploring side corridors and successfully returning to the main path.


*(Replace `images/task_b.png` with your screenshot or GIF)*

**Execution:**
Follow the same launch sequence as Task A, but use the **2D Goal Pose** tool to direct the robot into the side branches of the mapped corridor.

### Task C: Autonomous Corridor Coverage (Zigzag)

A custom Python finite state machine (FSM) utilizing time-based rotational calculations to perform a symmetric 170-degree Boustrophedon sweep of the corridor.


*(Replace `images/task_c.png` with your screenshot or GIF)*

**Execution:**

1. Launch the simulation:

   ```
   ros2 launch bot_simulation sim_bringup.launch.py
   
   ```

2. Run the custom coverage script:

   ```
   ros2 run bot_simulation coverage_cleaner.py
   
   ```

## Architecture & Troubleshooting Notes

This workspace implements specific architectural fixes to ensure stable simulation time synchronization between Gazebo and ROS 2:

* **One-Way TF Bridge:** The `/tf` and `/clock` topics utilize unidirectional bridging (`[`) to prevent time extrapolation loops.

* **Sim Time Enforcement:** All nodes, bridges, and Nav2 launch files strictly enforce `use_sim_time:=true`.

* **TF Tree Optimization:** The standard `joint_state_publisher` is bypassed in favor of native Gazebo differential drive joint broadcasting to eliminate 69ms latency timeouts in the global costmap.

## Repository Structure

* `/bot_simulation`: Contains the robot URDF (Xacro), custom Gazebo worlds (`corridor.sdf`), launch files, and the Task C Python FSM.

* `/bot_navigation`: Contains the generated maps (PGM/YAML) and Nav2 configurations.
