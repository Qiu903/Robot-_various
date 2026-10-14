import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from math import atan2, degrees, sqrt, radians, pi

class GazeboSquare(Node):
    # 想改车速/边长就改这几个数
    LIN_SPEED = 0.15            # 直行速度 m/s
    ANG_SPEED = 0.5             # 转向角速度 rad/s
    SIDE = 0.5                  # 正方形边长 m
    TARGET_TURN = radians(90)   # 每次转 90°

    def __init__(self):
        super().__init__('gazebo_square')

        self.sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # 下面这些是"车的当前状态"，由回调更新、由定时器读取
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.start_x = 0.0      # 本条边的起点
        self.start_y = 0.0
        self.start_yaw = 0.0    # 本次转向的起始角度

        self.state = 'FWD'      # 状态机：'FWD' 直行 / 'TURN' 转向
        self.side_count = 0     # 已走完的边数
        self.initialized = False

        self.timer = self.create_timer(0.1, self.control_loop)   # 10 Hz
        self.get_logger().info('GazeboSquare 启动')

    def odom_callback(self, msg):
        pos = msg.pose.pose.position
        ori = msg.pose.pose.orientation

        self.x = pos.x
        self.y = pos.y

        # 四元数 → yaw（上节课的通用公式，拆成两行写，方便对照）
        #   公式：yaw = atan2( 2*(w*z + x*y),  1 - 2*(y*y + z*z) )
        siny_cosp = 2.0 * (ori.w * ori.z + ori.x * ori.y)
        cosy_cosp = 1.0 - 2.0 * (ori.y * ori.y + ori.z * ori.z)
        self.yaw = atan2(siny_cosp, cosy_cosp)

        # 第一次收到 odom 时，把当前位置记为本条边的起点
        if not self.initialized:
            self.start_x = self.x
            self.start_y = self.y
            self.start_yaw = self.yaw
            self.initialized = True

    def control_loop(self):
        cmd = Twist()

        if self.state == 'FWD':
            # 已走距离 = 起点到当前位置的直线距离（勾股定理）
            dx = self.x - self.start_x
            dy = self.y - self.start_y
            moved = sqrt(dx * dx + dy * dy)

            if moved >= self.SIDE:
                # 这条边走够了 → 切到转弯，并把"当前角度"记为本次转向的起点
                self.state = 'TURN'
                self.start_yaw = self.yaw
                self.get_logger().info(f'第 {self.side_count + 1} 条边走完，开始转弯')
            else:
                cmd.linear.x = self.LIN_SPEED       # 还没走够，继续直行

        elif self.state == 'TURN':
            # 先算出角度差，再做"角度归一化"：
            # yaw 到 ±180° 会突然跳变，裸减法会算出 ±300° 这种假值
            # 所以把结果强行掰回 (-pi, pi] 区间：超了就减一整圈，少了就加一整圈
            turned = self.yaw - self.start_yaw
            while turned > pi:
                turned -= 2.0 * pi
            while turned < -pi:
                turned += 2.0 * pi

            if abs(turned) >= self.TARGET_TURN:
                # 转够了 → 回到直行，边数 +1，把当前位置记为下一条边的起点
                self.state = 'FWD'
                self.side_count += 1
                self.start_x = self.x
                self.start_y = self.y
                self.get_logger().info(f'转弯完成，已走完 {self.side_count} 条边')
            else:
                cmd.angular.z = self.ANG_SPEED      # 还没转够，继续转

        # 四条边走完就停车
        if self.side_count >= 4:
            cmd = Twist()

        self.pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = GazeboSquare()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()