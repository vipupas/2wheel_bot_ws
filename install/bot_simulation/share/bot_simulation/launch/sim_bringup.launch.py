import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = get_package_share_directory('bot_simulation')
    
    # Define paths to URDF and the custom world file
    urdf_file = os.path.join(pkg_dir, 'urdf', 'bot.urdf.xacro')
    world_file = os.path.join(pkg_dir, 'worlds', 'corridor.sdf') # <-- CHANGE NAME HERE IF NEEDED

    # Convert Xacro to standard XML
    doc = xacro.process_file(urdf_file)
    robot_desc = doc.toxml()

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    # Ignition Gazebo (Loading Custom World)
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        # Passes the -r flag and the absolute path to your custom world
        launch_arguments={'gz_args': f'-r {world_file}'}.items() 
    )

    # Spawn Robot
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', '2wheels_bot', '-string', robot_desc, '-x', '0.0', '-y', '0.0', '-z', '0.2'],
        output='screen'
    )

    # BYPASS GZ BRIDGE: Publish default wheel positions directly to ROS 2
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': True}]
    )

    # 1. DEDICATED CLOCK BRIDGE
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )


    # 2. DEDICATED SENSOR BRIDGE
    sensor_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/camera@sensor_msgs/msg/Image@gz.msgs.Image',
            
            # --- OTHER SENSORS ---
            '/imu@sensor_msgs/msg/Imu@gz.msgs.IMU',
            '/depth_camera_image@sensor_msgs/msg/Image@gz.msgs.Image',
            '/depth_camera_image/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
            '/ultrasonic/us_front_left@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/ultrasonic/us_front_right@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/ultrasonic/us_rear_left@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/ultrasonic/us_rear_right@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        gz_sim,
        spawn_robot,
        clock_bridge,
        joint_state_publisher,
        sensor_bridge
    ])