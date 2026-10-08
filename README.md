# 我的 ROS2 机器人学习记录

个人 ROS 2 学习过程记录，目标方向：机器人感知 → 具身智能。

## 环境
- Ubuntu 22.04 (WSL2)
- ROS 2 Humble
- Python 3.10

## 我学到了什么
- 通信模型：话题 = 发布/订阅的"暗号"，**话题名 + 消息类型都匹配**才会连上；写错话题名会**静默失败**（不报错但收不到数据）
- 静默失败 vs 当场报错：话题写错 → 沉默等待；import 模块拼错 → 当场崩溃（ModuleNotFoundError）
- `rclpy.spin(node)` 是**单线程事件调度员**：它负责检查定时器/消息/服务，有事件就调用对应回调；没有它节点不干活
- 回调里不能放 `time.sleep()` 等阻塞操作：单线程下会卡住整个节点，导致定时器触发被跳过后合并、机器人一顿一顿
- ROS2 Python 节点万能骨架：`class 节点类(Node)` + `def main()` + `if __name__ == "__main__"`；`main` 负责 init → 建节点 → spin → shutdown
- Twist 消息是两层结构：`linear.x`（前进速度）/ `angular.z`（角速度，绕 Z 轴转，正=逆时针）；ROS2 消息字段是强类型 float，整数要写成 `3.0`

## 我踩过的坑
- `from geometry_msgs.msgs import Twist` 拼错 → ModuleNotFoundError（正确是 `geometry_msgs.msg`）
- 缺 `if __name__ == "__main__": main()` → 文件被读取一遍但**什么都不执行**（静默失败）
- 给 `msg.linear.x = 3` 赋整数 → AssertionError，必须 `msg.linear.x = 3.0`
- 在回调里 `time.sleep(2)` → spin 单线程被卡死，海龟每 2 秒才跳一次半圈
- 忘记删除多余的 import（如 `turtlesim.msg`、`math`）→ 代码残留垃圾，读起来混乱

## 节点清单
- `pose_subscriber.py`：订阅 `/turtle1/pose` 并打印位姿
- `square_driver.py`：开环控制，盲发指令画正方形
- `closed_loop_square.py`：闭环旋转 90 度（P 控制）
- `closed_loop_square_full.py`：PI 控制 + 超时检测，画完整正方形
- `circle_drive.py`：发布 `/turtle1/cmd_vel`，让海龟画圆（第一个独立调试、亲手踩坑修好的节点）

## 运行方式
```bash
# 终端1：启动海龟仿真
ros2 run turtlesim turtlesim_node

# 终端2：运行某个控制节点
ros2 run my_robot_control closed_loop_square_full   # 画正方形
ros2 run my_robot_control circle_drive              # 画圆
```
