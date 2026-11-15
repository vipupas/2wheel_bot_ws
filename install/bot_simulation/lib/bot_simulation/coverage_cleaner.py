#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data

class ZigzagCleaner(Node):
    def __init__(self):
        super().__init__('coverage_cleaner')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, qos_profile_sensor_data)
            
        self.state = 'INIT_TURN_90'
        self.heading_left = True  # Tracks which wall we are driving towards
        self.front_dist = 10.0
        
        # Time-based turning calculations (Turn speed = 0.5 rad/s)
        self.start_time = self.get_clock().now().nanoseconds / 1e9
        self.time_90 = 1.57 / 0.5    # 3.14 seconds for 90 degrees
        self.time_170 = 2.967 / 0.5  # ~5.93 seconds for 170 degrees

        self.timer = self.create_timer(0.1, self.control_loop)

    def scan_callback(self, msg):
        # Grab a 30-degree cone directly in front of the robot (indices 165 to 195)
        front_ranges = msg.ranges[165:195]
        valid_ranges = [r for r in front_ranges if r > 0.1 and str(r) != 'inf' and str(r) != 'nan']
        if valid_ranges:
            self.front_dist = min(valid_ranges)

    def control_loop(self):
        msg = Twist()
        now = self.get_clock().now().nanoseconds / 1e9

        if self.state == 'INIT_TURN_90':
            # Initial 90-degree left turn to face the left wall
            if (now - self.start_time) < self.time_90:
                msg.angular.z = 0.5 # Positive is Left/Counter-Clockwise
            else:
                self.state = 'MOVE_FORWARD'

        elif self.state == 'MOVE_FORWARD':
            if self.front_dist > 0.5:
                msg.linear.x = 0.3
            else:
                self.state = 'TURN_170'
                self.start_time = now

        elif self.state == 'TURN_170':
            if self.heading_left:
                # Arrived at Left Wall: Turn 170 degrees RIGHT (Clockwise)
                if (now - self.start_time) < self.time_170:
                    msg.angular.z = -0.5
                else:
                    self.state = 'MOVE_FORWARD'
                    self.heading_left = False # Now heading to the right wall
            else:
                # Arrived at Right Wall: Turn 170 degrees LEFT (Counter-Clockwise)
                if (now - self.start_time) < self.time_170:
                    msg.angular.z = 0.5
                else:
                    self.state = 'MOVE_FORWARD'
                    self.heading_left = True # Now heading back to the left wall

        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ZigzagCleaner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()