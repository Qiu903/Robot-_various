# ROS 2 学习记录

## 环境
- Ubuntu 22.04 (WSL2)
- ROS 2 Humble
- Python 3.10

## 包含节点
- `pose_subscriber.py`：订阅 `/turtle1/pose` 并打印位姿
- `square_driver.py`：开环控制，盲发指令画正方形
- `closed_loop_square.py`：闭环旋转90度（P控制）
- `closed_loop_square_full.py`：PI控制 + 超时检测，画完整正方形

## 运行方式
```bash
ros2 run turtlesim turtlesim_node
ros2 run my_robot_control closed_loop_square_full
本仓库为个人 ROS 2 学习过程记录。祝各位无限进步。
