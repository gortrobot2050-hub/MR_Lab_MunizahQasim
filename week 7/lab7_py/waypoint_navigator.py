import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped

class WaypointNavigator(Node):
    def __init__(self):
        super().__init__('waypoint_navigator')
        self._client = ActionClient(self, FollowWaypoints, 'follow_waypoints')

    def send_waypoints(self, waypoints):
        self.get_logger().info('Waiting for FollowWaypoints action server...')
        self._client.wait_for_server()
        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = waypoints
        self.get_logger().info(f'Sending {len(waypoints)} waypoints...')

        print('\n========== WAYPOINT MISSION STARTED ==========')
        for i, wp in enumerate(waypoints):
            print(f'  Waypoint {i+1}: x={wp.pose.position.x}, y={wp.pose.position.y}')
        print('==============================================\n')

        send_goal_future = self._client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)
        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by server!')
            return

        self.get_logger().info('Goal accepted. Navigating...')
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        print('\n========== MISSION COMPLETE ==========')
        print('All waypoints reached successfully!')
        print('======================================\n')

    def feedback_callback(self, feedback_msg):
        current = feedback_msg.feedback.current_waypoint
        print(f'>>> Navigating to Waypoint {current + 1}...')

def make_pose(x, y, yaw_w):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = 0.0
    pose.pose.orientation.z = yaw_w
    pose.pose.orientation.w = 1.0
    return pose

def main(args=None):
    rclpy.init(args=args)
    navigator = WaypointNavigator()
    waypoints = [
        make_pose(0.5,  0.0,  1.0),  # Waypoint 1
        make_pose(1.5,  0.0,  1.0),  # Waypoint 2
        make_pose(1.5,  1.0,  1.0),  # Waypoint 3
        make_pose(0.0,  1.0,  1.0),  # Waypoint 4
        make_pose(0.0,  0.0,  1.0),  # Waypoint 5
    ]
    navigator.send_waypoints(waypoints)
    navigator.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
