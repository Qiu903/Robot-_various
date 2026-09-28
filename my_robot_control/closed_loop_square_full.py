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
        self.side_length = 2.0
        self.target_angle = 0.0
        self.start_x = 0.0
        self.start_y = 0.0
        self.step_count = 0
        self.angle_integral = 0.0
        self.last_pose_time = 0.0

    def pose_callback(self, msg):
        self.current_pose = msg
        self.last_pose_time = self.get_clock().now().nanoseconds / 1e9

    def timer_callback(self):
        if self.current_pose is None:
            return
        now = self.get_clock().now().nanoseconds / 1e9
        if now - self.last_pose_time > 1.0:
            msg = Twist()
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.publisher_.publish(msg)
            self.get_logger().warn('传感器数据超时，已停止发送指令')
            return
        msg = Twist()
        if self.state == 'WAIT':
            self.start_x = self.current_pose.x
            self.start_y = self.current_pose.y
            self.target_angle = self.current_pose.theta + math.pi / 2
            self.angle_integral = 0.0
            self.state = 'TURN'
            self.get_logger().info('开始执行正方形轨迹...')
        elif self.state == 'TURN':
            angle_diff = self.target_angle - self.current_pose.theta
            if angle_diff > math.pi: angle_diff -= 2 * math.pi
            if angle_diff < -math.pi: angle_diff += 2 * math.pi
            self.angle_integral += angle_diff * 0.1
            msg.angular.z = 2.0 * angle_diff + 0.5 * self.angle_integral
            if abs(angle_diff) < 0.005:
                msg.angular.z = 0.0
                self.angle_integral = 0.0
                self.start_x = self.current_pose.x
                self.start_y = self.current_pose.y
                self.state = 'FORWARD'
                self.get_logger().info(f'转弯完成 | 边数: {self.step_count} | 误差: {angle_diff:.6f}')
        elif self.state == 'FORWARD':
            distance = math.sqrt((self.current_pose.x - self.start_x)**2 + (self.current_pose.y - self.start_y)**2)
            if distance < self.side_length - 0.05:
                msg.linear.x = 1.5 * (self.side_length - distance)
            else:
                msg.linear.x = 0.0
                self.step_count += 1
                if self.step_count >= 4:
                    self.state = 'DONE'
                    self.get_logger().info('正方形轨迹完成！')
                else:
                    self.target_angle = self.current_pose.theta + math.pi / 2
                    self.state = 'TURN'
                    self.get_logger().info(f'第 {self.step_count} 条边直行完成，准备转弯')
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ClosedLoopSquare()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
