import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
import math

class FollowLeader(Node):
    def __init__(self):
        super().__init__('follow_leader')

        self.leader_pose = None
        self.follower_pose = None

        self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.leader_callback,
            10
        )

        self.create_subscription(
            Pose,
            '/turtle2/pose',
            self.follower_callback,
            10
        )

        self.pub = self.create_publisher(
            Twist,
            '/turtle2/cmd_vel',
            10
        )

    def leader_callback(self, msg):
        self.leader_pose = msg
        self.move()

    def follower_callback(self, msg):
        self.follower_pose = msg

    def move(self):
        if self.leader_pose is None or self.follower_pose is None:
            return

        cmd = Twist()

        # distance between turtles
        dx = self.leader_pose.x - self.follower_pose.x
        dy = self.leader_pose.y - self.follower_pose.y
        distance = math.sqrt(dx**2 + dy**2)

        # angle to leader
        angle_to_leader = math.atan2(dy, dx)

        # angle difference
        angle_diff = angle_to_leader - self.follower_pose.theta

        # normalize angle
        angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))

        # control
        cmd.linear.x = 2.0 * distance
        cmd.angular.z = 6.0 * angle_diff

        self.pub.publish(cmd)


def main():
    rclpy.init()
    node = FollowLeader()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
