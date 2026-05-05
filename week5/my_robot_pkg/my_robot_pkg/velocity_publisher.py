import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class VelocityPublisher(Node):

    def __init__(self):
        super().__init__('velocity_publisher')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(2.0, self.timer_callback)
        self.toggle = True

    def timer_callback(self):
        msg = Twist()

        if self.toggle:
            msg.linear.x = 0.2   # forward velocity
            self.get_logger().info('Moving forward')
        else:
            msg.linear.x = 0.0   # stop
            self.get_logger().info('Stopping')

        self.publisher_.publish(msg)
        self.toggle = not self.toggle


def main(args=None):
    rclpy.init(args=args)
    node = VelocityPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
