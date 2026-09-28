import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

class ClosedLoopSquare(Node):
    def __init__(self):
        super().__init__('closed_loop_square')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.current_pose = None
        self.state = 'WAIT'
        self.target_angle = 0.0

    def pose_callback(self, msg):
        self.current_pose = msg

    def timer_callback(self):
        if self.current_pose is None:
            return
        msg = Twist()
        if self.state == 'WAIT':
            self.target_angle = self.current_pose.theta + math.pi / 2
            self.state = 'ROTATE'
            self.get_logger().info('开始旋转...')
        elif self.state == 'ROTATE':
            angle_diff = self.target_angle - self.current_pose.theta
            if angle_diff > math.pi: angle_diff -= 2 * math.pi
            if angle_diff < -math.pi: angle_diff += 2 * math.pi
            if abs(angle_diff) > 0.05:
                msg.angular.z = 1.0 * angle_diff
            else:
                msg.angular.z = 0.0
                self.state = 'DONE'
                self.get_logger().info(f'旋转完成！最终误差：{angle_diff:.4f} 弧度')
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ClosedLoopSquare()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
