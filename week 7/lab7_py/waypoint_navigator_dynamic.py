import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped
import sys

class WaypointNavigator(Node):
    def __init__(self):
        super().__init__('waypoint_navigator')
        self._client = ActionClient(self, FollowWaypoints, 'follow_waypoints')

    def send_waypoints(self, waypoints):
        self.get_logger().info('Waiting for FollowWaypoints action server...')
        self._client.wait_for_server()
        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = waypoints

        print('\n========== DYNAMIC WAYPOINT MISSION ==========')
        for i, wp in enumerate(waypoints):
            print(f'  Waypoint {i+1}: x={wp.pose.position.x}, y={wp.pose.position.y}')
        print('===============================================\n')

        send_goal_future = self._client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)
        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected!')
            return

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        print('\n========== MISSION COMPLETE ==========')
        print('All waypoints reached!')
        print('======================================\n')

    def feedback_callback(self, feedback_msg):
        current = feedback_msg.feedback.current_waypoint
        print(f'>>> Navigating to Waypoint {current + 1}...')

def make_pose(x, y, w):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.position.z = 0.0
    pose.pose.orientation.z = float(w)
    pose.pose.orientation.w = 1.0
    return pose

def main():
    args = sys.argv[1:]
    if len(args) == 0 or len(args) % 3 != 0:
        print('Usage: python3 waypoint_navigator_dynamic.py x1 y1 w1 x2 y2 w2 ...')
        print('Example: python3 waypoint_navigator_dynamic.py 0.5 0.0 1.0 1.5 0.0 1.0')
        return

    rclpy.init()
    navigator = WaypointNavigator()

    waypoints = []
    for i in range(0, len(args), 3):
        x, y, w = args[i], args[i+1], args[i+2]
        waypoints.append(make_pose(x, y, w))
        print(f'Parsed Waypoint {i//3 + 1}: x={x}, y={y}, w={w}')

    navigator.send_waypoints(waypoints)
    navigator.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
