#!/usr/bin/env python3
import rospy
import yaml
import importlib
import csv
import os
import time
import threading
import matplotlib.pyplot as plt
import numpy as np
from std_msgs.msg import Header

# ========== 动态访问嵌套字段 ==========
def extract_field(msg, field_path):
    val = msg
    for attr in field_path.split('.'):
        val = getattr(val, attr, None)
        if val is None:
            return None
    return val

# ========== 加载 YAML 配置 ==========
def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

# ========== 主类 ==========
class ROSDataLogger:
    def __init__(self, config):
        self.topic = config['topic_name']
        self.fields = config['fields']
        self.rate = config.get('rate', 10)
        self.buffer = []
        self.timestamps = []
        self.csv_file = self.init_csv()
        self.lock = threading.Lock()
        self.last_row = None
        self.outlier_threshold = config.get('outlier_threshold', 100)  # 可在yaml中配置

        pkg, msg_type = config['msg_type'].split('/')
        msg_module = importlib.import_module(f'{pkg}.msg')
        self.msg_class = getattr(msg_module, msg_type)

        rospy.Subscriber(self.topic, self.msg_class, self.callback)

    def init_csv(self):
        os.makedirs('output', exist_ok=True)
        ts = time.strftime('%Y%m%d_%H%M%S')
        path = f'output/data_log_{ts}.csv'
        f = open(path, 'w', newline='')
        writer = csv.writer(f)
        writer.writerow(['time'] + self.fields)
        self.csv_writer = writer
        return f

    def is_outlier(self, row):
        # 剔除NaN/inf
        if any(val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))) for val in row):
            return True
        # 剔除突变
        if self.last_row is not None:
            diffs = [abs((a if a is not None else 0) - (b if b is not None else 0)) for a, b in zip(row, self.last_row)]
            if any(d > self.outlier_threshold for d in diffs):
                return True
        return False

    def callback(self, msg):
        row = []
        for field in self.fields:
            val = extract_field(msg, field)
            row.append(val)
        now = rospy.Time.now().to_sec()
        if self.is_outlier(row):
            rospy.logwarn(f"异常值剔除: {row}")
            return
        with self.lock:
            self.csv_writer.writerow([now] + row)
            self.timestamps.append(now)
            self.buffer.append(row)
            self.last_row = row

    def close(self):
        self.csv_file.close()

# ========== 实时绘图 ==========
def live_plot(logger):
    plt.ion()
    fig, ax = plt.subplots()
    lines = [ax.plot([], [], label=f)[0] for f in logger.fields]
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Value')
    ax.legend()
    outlier_points = [[] for _ in logger.fields]
    outlier_times = [[] for _ in logger.fields]
    while not rospy.is_shutdown():
        with logger.lock:
            if len(logger.timestamps) < 2:
                continue
            x = logger.timestamps[-100:]
            y_data = list(zip(*logger.buffer))  # fields × samples
        for i, line in enumerate(lines):
            line.set_xdata(x)
            line.set_ydata(y_data[i][-100:])
        ax.relim()
        ax.autoscale()
        plt.pause(0.05)

# ========== 启动节点 ==========
if __name__ == '__main__':
    rospy.init_node('data_logger_node')
    config = load_config(os.path.join(os.path.dirname(__file__), '../config/topic_config.yaml'))
    logger = ROSDataLogger(config)

    plot_thread = threading.Thread(target=live_plot, args=(logger,))
    plot_thread.daemon = True
    plot_thread.start()

    rospy.spin()
    logger.close()
