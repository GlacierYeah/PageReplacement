# PageReplacement
页面置换算法模拟器

## 项目概述

本项目是一个页面置换算法模拟器，旨在模拟不同页面置换算法（FIFO、LRU、OPT、LFU）在处理页面访问序列时的行为。通过该模拟器，用户可以直观地观察各种算法在不同内存大小、是否使用快表等条件下的性能表现，包括缺页次数、缺页率、总时间和平均时间等指标。

## 项目功能

1. **多种算法模拟**：支持先进先出（FIFO）、最近最少使用（LRU）、最优（OPT）和最少使用频次（LFU）四种页面置换算法的模拟。
2. **参数设置**：用户可以自定义内存大小、是否使用快表以及页面访问序列。
3. **可视化展示**：以图形化界面展示每个算法的内存状态、快表状态、缺页情况和访问历史记录。
4. **性能统计**：统计并显示每个算法的缺页次数、缺页率、总时间和平均时间，并提供算法性能对比表格。
5. **模拟控制**：支持开始、暂停、停止模拟操作，以及调整模拟速度。
6. **结果导出**：用户可以将模拟结果导出为文本文件，方便后续分析。

## 项目结构

plaintext











```plaintext
PageReplacement/
├── FlaskProject/
│   ├── .idea/                   # IDE 配置文件
│   │   ├── misc.xml
│   │   ├── modules.xml
│   │   ├── inspectionProfiles/
│   │   │   ├── profiles_settings.xml
│   │   │   └── Project_Default.xml
│   │   ├── deployment.xml
│   │   └── .gitignore
│   ├── algorithms.py            # 页面置换算法实现
│   ├── app.py                   # Flask 应用主文件
│   └── templates/
│       └── index.html           # 前端页面文件
└── README.md                    # 项目说明文件
```

## 运行步骤

在项目根目录下，进入 `FlaskProject` 文件夹，运行以下命令启动 Flask 应用：

bash











```bash
cd PageReplacement/FlaskProject
python app.py
```
