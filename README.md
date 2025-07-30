# ROS Data Logger & Visualizer

本项目用于订阅 ROS 中的任意话题，自动记录消息数据为 CSV 文件，并提供实时可视化功能，方便机器人调试与数据分析。

## ✨ 功能特性

- ✅ 支持自定义订阅话题及字段
- ✅ 实时记录数据并保存为 CSV
- ✅ 支持简单异常值剔除（如NaN/突变）
- ✅ 可视化指定字段随时间变化的曲线
- ✅ 支持通过YAML配置文件指定话题及参数

## 🚀 使用方式

1. 修改 `config/topic_config.yaml` 指定订阅话题名、字段等参数
2. 启动 ROS 核心：

```bash
roscore
```

3. 启动数据记录节点：

```bash
rosrun ros_data_logger_visualizer data_logger.py
```

或直接用 Python 运行：

```bash
python3 scripts/data_logger.py
```

4. 运行后会在 `output/` 目录下自动生成 CSV 文件，并弹出实时曲线窗口。

## ⚙️ 配置说明

`config/topic_config.yaml` 示例：

```yaml
topic_name: "/your_topic_name"
msg_type: "std_msgs/Float32MultiArray"
fields:
  - "data[0]"
  - "data[1]"
rate: 10
```

- `topic_name`：要订阅的 ROS 话题名
- `msg_type`：消息类型（如 std_msgs/Float32MultiArray）
- `fields`：要记录的字段（支持嵌套，如 header.stamp）
- `rate`：采样频率（Hz）

## 🛡️ 异常值剔除

- 自动剔除 NaN、inf、以及与前一帧差异过大的异常值（可在代码中调整阈值）

## 🖥️ 依赖安装

```bash
pip install -r requirements.txt
```

## 📝 目录结构

```
ros_data_logger_visualizer/
├── config/
│   └── topic_config.yaml
├── launch/
│   └── data_logger.launch
├── output/
├── scripts/
│   └── data_logger.py
├── requirements.txt
└── README.md
```

## 🧩 其他

- 支持自定义消息类型（需已编译对应 ROS msg）
- 可根据需要扩展异常值处理、可视化等功能
