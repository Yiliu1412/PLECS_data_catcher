# PLECS Data Catcher

[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

🔌 PLECS 电力电子仿真参数扫描与数据自动采集工具（基于 XML-RPC）

---

## 📋 项目简介

PLECS Data Catcher 是一个用于自动化 PLECS 仿真的 Python 工具，支持：

- ✅ **参数扫描**：自动遍历多个参数组合进行批量仿真
- ✅ **自动仿真**：通过 XML-RPC 接口调用 PLECS 引擎
- ✅ **数据采集**：自动提取和整理仿真生成的 CSV 数据
- ✅ **结果管理**：为每次仿真生成独立的数据文件，便于后续分析

适用于电力电子系统（如逆变器、DC-DC变换器等）的性能评估和参数优化。

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- PLECS Standalone 或 PLECS Blockset（需启用 XML-RPC Server）
- 无第三方 Python 包依赖（当前脚本仅使用标准库）

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd PLCES_data_catcher
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   # 使用 Conda
   conda create -n plecs_env python=3.10
   conda activate plecs_env
   
   # 或使用 venv
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   # 当前 requirements.txt 无需安装额外包，可跳过此步骤
   pip install -r requirements.txt
   ```

### 配置 PLECS

在运行脚本前，请确保 PLECS XML-RPC Server 已启动：

1. 打开 PLECS
2. 菜单栏选择：`Tools` → `XML-RPC Server` → `Start Server`
3. 确认服务器运行在 `http://127.0.0.1:1080/RPC2`

---

## 💻 使用方法

### 基本用法

```bash
python src/plecs_data_catcher.py
```

### 配置参数扫描

在 `src/plecs_data_catcher.py` 中修改扫描参数：

```python
# 参数扫描范围（根据你的模型修改）
SCAN_PARAMETERS = {
    "Udc": [350, 400, 450],              # DC 总线电压 (V)
    "f_sw": [15000, 18000, 21000],      # 开关频率 (Hz)
}
```

### 指定模型文件

```python
MODEL_FILE = PROJECT_ROOT / "py_grid_connected_convert.plecs"
```

---

## 📂 项目结构

```
PLCES_data_catcher/
├── src/
│   └── plecs_data_catcher.py    # 主脚本
├── outputs/                      # 输出目录（自动生成）
│   ├── sim_data.csv             # 合并的仿真数据
│   └── sim_data_run_*.csv       # 各次仿真的原始数据
├── requirements.txt              # 依赖清单（当前无第三方依赖）
├── README.md                     # 项目说明
└── LICENSE                       # 许可证

```

---

## 📊 输出说明

运行成功后，会在 `outputs/` 目录生成以下文件：

### 1. 分离的仿真数据
每次仿真生成独立的 CSV 文件：
```
sim_data_run_001__Udc_350__f_sw_15000.csv
sim_data_run_002__Udc_350__f_sw_18000.csv
sim_data_run_003__Udc_350__f_sw_21000.csv
...
```

### 2. 合并数据（可选）
所有仿真数据合并到：
```
sim_data.csv
```

---

## 🔧 工作原理

1. **连接 PLECS**：通过 XML-RPC 连接到 PLECS 服务器
2. **加载模型**：使用 `plecs.load()` 加载指定的 `.plecs` 文件
3. **参数设置**：使用 `plecs.set()` 修改模型参数
4. **执行仿真**：调用 `plecs.simulate()` 运行仿真
5. **数据采集**：从指定位置读取生成的 CSV 文件
6. **结果保存**：重命名并保存到 `outputs/` 目录

---

## ⚙️ 常见问题

### Q: 报错 "Connection refused"
**A:** 请确保 PLECS XML-RPC Server 已启动。在 PLECS 中执行：
   - `Tools` → `XML-RPC Server` → `Start Server`

### Q: 报错 "Invalid model name"
**A:** 可能的原因：
   - 模型文件路径不正确
   - 模型名称与脚本中的不一致
   - 需要在每次仿真后重新加载模型

### Q: 找不到 CSV 文件
**A:** 检查以下位置：
   - PLECS 模型中 Scope 的输出路径设置
   - `CSV_SOURCE_CANDIDATES` 中配置的候选路径

## 🌟 致谢

- [PLECS](https://www.plexim.com/) - 专业的电力电子仿真软件
- 感谢所有贡献者的支持


