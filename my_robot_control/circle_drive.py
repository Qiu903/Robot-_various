import rclpy
import time
from rclpy.node import Node
from geometry_msgs.msg import Twist

class Circle_Drive(Node):
    def __init__(self):
        super().__init__("circledrive")
        self.pub=self.create_publisher(Twist,"turtle1/cmd_vel",10)
        self.timer=self.create_timer(0.1,self.timer_callback)

    def timer_callback(self):
        time.sleep(2)
        msg =Twist()
        msg.linear.x=3.0
        msg.angular.z=3.0
        self.pub.publish(msg)
        self.get_logger().info(f"发布指令：{msg}")


def main(args=None):
        rclpy.init(args=args)
        node=Circle_Drive()
        rclpy.spin(node)
        rclpy.shutdown()

if __name__ == "__main__":
    main()