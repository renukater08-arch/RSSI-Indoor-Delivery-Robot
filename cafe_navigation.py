
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped


class CafeNavigation(Node):

    def __init__(self):
        super().__init__('cafe_navigation')

        self.publisher = self.create_publisher(
            Twist,
            '/model/cafe_delivery_robot/cmd_vel',
            10
        )

        self.subscription = self.create_subscription(
            Odometry,
            '/model/cafe_delivery_robot/odometry',
            self.odom_callback,
            10
        )
        self.path_publisher = self.create_publisher(
            Path,
            '/robot_path',
             10
        )

        self.path_msg = Path()
        self.path_msg.header.frame_id = 'cafe_delivery_robot/odom'

        # Waypoints are relative to the robot's starting position.
        self.waypoints = [
            (7.9, 0.0),
            (7.9, 5.6),
            (7.4, 5.6)
        ]
        self.planned_path_publisher = self.create_publisher(
            Path,
            '/planned_path',
            10
        )

        self.planned_path = Path()
        self.planned_path.header.frame_id = 'cafe_delivery_robot/odom'

        # Include the starting position and all destination waypoints.
        for x, y in [(0.0, 0.0)] + self.waypoints:
            pose = PoseStamped()
            pose.header.frame_id = 'cafe_delivery_robot/odom'
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.position.z = 0.05
            pose.pose.orientation.w = 1.0
            self.planned_path.poses.append(pose)

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.odom_received = False
        self.current_waypoint = 0
        self.finished = False

        self.timer = self.create_timer(0.1, self.navigate)

        self.get_logger().info('Cafe navigation node started.')

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation

        self.yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )
        pose = PoseStamped()
        pose.header = msg.header
        pose.header.frame_id = 'cafe_delivery_robot/odom'
        pose.pose = msg.pose.pose

        self.path_msg.header.stamp = msg.header.stamp
        self.path_msg.poses.append(pose)

        self.path_publisher.publish(self.path_msg)

        self.odom_received = True

    def publish_velocity(self, linear, angular):
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        self.publisher.publish(msg)

    def navigate(self):

        if not self.odom_received or self.finished:
            self.publish_velocity(0.0, 0.0)
            return

        if self.current_waypoint >= len(self.waypoints):
            self.stop_robot()
            return

        target_x, target_y = self.waypoints[self.current_waypoint]

        dx = target_x - self.x
        dy = target_y - self.y

        distance = math.hypot(dx, dy)

        # Check whether the current waypoint has been reached.
        if distance < 0.18:
            self.publish_velocity(0.0, 0.0)

            self.get_logger().info(
                f'Reached waypoint {self.current_waypoint + 1}'
            )

            self.current_waypoint += 1

            if self.current_waypoint >= len(self.waypoints):
                self.stop_robot()

            return
        self.planned_path.header.stamp = self.get_clock().now().to_msg()
        
        for pose in self.planned_path.poses:
            pose.header.stamp = self.planned_path.header.stamp
        
        self.planned_path_publisher.publish(self.planned_path)

        # Calculate the direction towards the next waypoint.
        desired_yaw = math.atan2(dy, dx)

        angle_error = math.atan2(
            math.sin(desired_yaw - self.yaw),
            math.cos(desired_yaw - self.yaw)
        )

        # Turn first, then move forward.
        if abs(angle_error) > 0.18:
            linear_velocity = 0.0
            angular_velocity = 0.35 if angle_error > 0 else -0.35

        else:
            linear_velocity = 0.12
            angular_velocity = max(
                -0.25,
                min(0.25, 1.0 * angle_error)
            )

        self.publish_velocity(
            linear_velocity,
            angular_velocity
        )

    def stop_robot(self):
        self.publish_velocity(0.0, 0.0)

        if not self.finished:
            self.finished = True
            self.get_logger().info(
                'Destination reached. Robot stopped.'
            )


def main(args=None):
    rclpy.init(args=args)

    node = CafeNavigation()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        node.get_logger().info('Navigation interrupted.')

    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
