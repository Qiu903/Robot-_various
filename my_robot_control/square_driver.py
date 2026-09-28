import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class SquareDriver(Node):
    def __init__(self):
        super().__init__('square_driver')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.state = 0
        self.counter = 0

    def timer_callback(self):
        msg = Twist()
        if self.state == 0:
            msg.linear.x = 2.0
            msg.angular.z = 0.0
            self.counter += 1
            if self.counter >= 20:
                self.state = 1
                self.counter = 0
        else:
            msg.linear.x = 0.0
            msg.angular.z = 1.0
            self.counter += 1
            if self.counter >= 16:
                self.state = 0
                self.counter = 0
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SquareDriver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
