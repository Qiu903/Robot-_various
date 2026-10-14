import rclpy
from rclpy.node import Node

from example_interfaces.srv import AddTwoInts


class AddServerNode(Node):
    def __init__(self):
        super().__init__("add_server")

        self.srv=self.create_service(
            AddTwoInts,
            "add_two_ints",
            self.add_callback
        )
        self.get_logger().info("加法服务启动，等待请求。。。。")

    def add_callback(self, req, resp):
        resp.sum = req.a + req.b

        self.get_logger().info(
            f"收到请求：a={req.a},b={req.b},计算结果：{resp.sum}"
        )

        return resp
        
def main(args=None):
    rclpy.init(args=args)
    node = AddServerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()