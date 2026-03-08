# PLECS Data Catcher

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PLECS](https://img.shields.io/badge/PLECS-XML--RPC-orange.svg)](https://www.plexim.com/)

🔌 **PLECS 电力电子仿真参数扫描与数据自动采集工具**（基于 XML-RPC）

---

## 📋 项目简介

**PLECS Data Catcher** 是一个用于自动化 PLECS 仿真的 Python 工具集，专为电力电子系统（如并网逆变器、DC-DC变换器、IGBT模块等）的参数优化与性能评估而设计。

### 核心功能

- ✅ **批量参数扫描**：自动遍历多维参数空间（电压、频率、温度、负载等）
- ✅ **自动化仿真**：通过 XML-RPC 接口无缝调用 PLECS 仿真引擎
- ✅ **智能数据采集**：自动提取、重命名并归档仿真生成的 CSV 数据
- ✅ **结果标准化管理**：为每组参数生成独立的数据文件，支持后续数据分析
- ✅ **可扩展架构**：支持集成机器学习模型（如 LSTM）进行结温预测等高级应用

### 典型应用场景

- 🔬 **IGBT/MOSFET 器件特性分析**：不同工况下的损耗、结温变化规律
- ⚡ **逆变器性能优化**：PWM 频率、调制深度对效率的影响
- 🌡️ **热管理设计**：环境温度与散热方案的评估
- 📈 **数据驱动建模**：为机器学习模型准备大规模训练数据

---

## 🚀 快速开始

### 环境要求

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| **Python** | 3.10+ | 推荐 3.11 或 3.13 |
| **PLECS** | 4.0+ | 需 Standalone 版本或 Blockset（Simulink） |
| **操作系统** | Windows/Linux/macOS | 已在 Windows 11 测试 |

> **注意**：数据采集脚本 (`plecs_data_catcher.py`) **仅使用 Python 标准库**，无需安装第三方包。  
> `requirements.txt` 中的依赖用于数据分析和机器学习模型训练（可选）。

---

### 安装步骤

#### 1. 克隆仓库

```bash
git clone <repository-url>
cd PLCES_data_catcher
```

#### 2. 创建虚拟环境（推荐）

**使用 Conda：**
```bash
conda create -n plecs_env python=3.11
conda activate plecs_env
```

**使用 venv：**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. 安装依赖（可选）

**仅运行数据采集**（无需安装任何包）：
```bash
python src/plecs_data_catcher.py
```

**完整功能**（数据分析 + 机器学习）：
```bash
pip install -r requirements.txt
```

**最小依赖**（仅数据处理）：
```bash
pip install numpy pandas matplotlib
```

---

### 配置 PLECS XML-RPC Server

在运行脚本前，必须启动 PLECS 的 XML-RPC 服务：

#### 方法 1：通过 GUI 启动（推荐）
1. 打开 PLECS 软件
2. 菜单栏：`Tools` → `XML-RPC Server` → `Start Server`
3. 确认控制台显示：`XML-RPC Server running on http://127.0.0.1:1080/RPC2`

#### 方法 2：通过脚本自动启动（PLECS 4.5+）
在 PLECS 命令窗口执行：
```matlab
xmlrpc.start('port', 1080)
```

#### 验证连接
运行以下 Python 代码测试连接：
```python
import xmlrpc.client
proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:1080/RPC2")
print(proxy.system.listMethods())
```

---

## 💻 使用方法

### 基本用法

```bash
python src/plecs_data_catcher.py
```

**运行流程**：
1. 连接到 PLECS XML-RPC 服务
2. 加载指定的 `.plecs` 模型文件
3. 遍历参数组合网格（由 `SCAN_PARAMETERS` 定义）
4. 对每组参数执行仿真并采集 CSV 数据
5. 将结果保存到 `outputs/` 目录

---

### 配置参数扫描

编辑 [src/plecs_data_catcher.py](src/plecs_data_catcher.py) 中的参数扫描配置：

```python
# 参数扫描范围（根据实际模型调整）
SCAN_PARAMETERS = {
    "Udc": [350, 400, 450],              # DC 总线电压 (V)
    "f_sw": [15000, 18000, 21000],      # 开关频率 (Hz)
    "R": [8, 10, 12],                    # 负载电阻 (Ohm)
    "environ_T": [25, 40, 55],           # 环境温度 (degC)
}
```

#### 参数说明

| 参数名 | 物理含义 | 典型范围 | 对系统的影响 |
|--------|---------|---------|-------------|
| `Udc` | 直流母线电压 | 300-600V | 决定变换器输出功率等级和开关损耗 |
| `f_sw` | PWM 开关频率 | 5-50kHz | 影响开关损耗、滤波器设计、EMI性能 |
| `R` | 负载电阻 | 5-20Ω | R↓ → 电流↑ → 导通损耗↑ → 结温↑ |
| `environ_T` | 环境/散热器温度 | -40~85°C | 影响器件热阻和结温上升 |

> **示例**：上述配置将产生 3×3×3×3 = **81 组仿真任务**。

---

### 指定模型文件

在脚本中修改模型路径：

```python
MODEL_FILE = PROJECT_ROOT / "your_model_name.plecs"
```

**自动查找逻辑**：
1. 优先查找项目根目录下的 `.plecs` 文件
2. 如未找到，尝试查找父目录（支持嵌套项目结构）

---

### 自定义输出路径

修改 CSV 查找位置（适用于 PLECS Scope 输出路径不在默认位置的情况）：

```python
CSV_SOURCE_CANDIDATES = [
    PROJECT_ROOT / "sim_data.csv",
    PROJECT_ROOT.parent / "sim_data.csv",
    pathlib.Path("D:/custom_output/sim_data.csv"),  # 自定义路径
]
```
MODEL_FILE = PROJECT_ROOT / "py_grid_connected_convert.plecs"
```

---

## 📂 项目结构

```
PLCES_data_catcher/
├── src/
│   ├── plecs_data_catcher.py    # 主脚本：参数扫描与数据采集
│   └── __pycache__/              # Python 缓存目录
├── outputs/                      # 输出目录（自动生成）
│   ├── sim_data_run_001__*.csv  # 各次仿真的原始数据（带参数标签）
│   ├── sim_data_run_002__*.csv
│   ├── ...
│   ├── sim_data.csv             # 最新一次仿真的数据副本
│   ├── igbt_lstm_model.pt       # 训练好的 LSTM 模型（可选）
│   └── igbt_lstm_meta.json      # 模型元数据（可选）
├── ref/
│   └── xmlrpc_controller_design.pdf  # PLECS XML-RPC 接口参考文档
├── requirements.txt              # Python 依赖清单
├── README.md                     # 项目说明文档（本文件）
├── LICENSE                       # 开源许可证
└── *.plecs                       # PLECS 仿真模型（用户自定义）
```

### 关键文件说明

| 文件/目录 | 功能描述 |
|----------|---------|
| `plecs_data_catcher.py` | 核心脚本，执行参数扫描、仿真调度和数据采集 |
| `outputs/sim_data_run_*.csv` | 每次仿真的时序数据（电压、电流、功率、温度等） |
| `ref/xmlrpc_controller_design.pdf` | PLECS 官方 XML-RPC API 文档 |

---

## 📊 输出说明

### 文件命名规则

每次仿真生成的 CSV 文件名包含完整的参数信息：

```
sim_data_run_{序号}__{参数1}_{值1}__{参数2}_{值2}__...csv
```

**示例**：
```
sim_data_run_001__Udc_350__environ_T_25__f_sw_15000.csv
sim_data_run_002__Udc_350__environ_T_40__f_sw_15000.csv
sim_data_run_027__Udc_450__environ_T_55__f_sw_21000.csv
```

### ❌ 错误：Connection refused / 连接被拒绝

**问题描述**：
```
[ERROR] 无法连接到 PLECS XML-RPC 服务
ConnectionRefusedError: [WinError 10061] 无法连接...
```

**解决方案**：
1. **确认 PLECS 已启动**：打开 PLECS 软件主界面
2. **启动 XML-RPC Server**：
   - GUI 方式：`Tools` → `XML-RPC Server` → `Start Server`
   - 命令方式：在 PLECS 命令窗口执行 `xmlrpc.start('port', 1080)`
3. **检查端口占用**：确保端口 `1080` 未被其他程序占用
4. **防火墙设置**：允许 Python 和 PLECS 通过本地端口通信

---

### ❌ 错误：Invalid model name / 模型名称无效

**问题描述**：
```
[WARN] 仿真调用失败: Fault -1: 'Invalid model name'
```

**可能原因**：
1. **模型未加载**：检查脚本日志中是否有 `[OK] 已调用 plecs.load`
2. **模型名称不匹配**：确保 `MODEL_FILE.stem` 与 PLECS 中的模型名称一致
3. **路径包含非 ASCII 字符**：尝试将项目移动到纯英文路径

**解决方案**：
```python
# 方法 1：使用绝对路径
MODEL_FILE = pathlib.Path("C:/Projects/my_model.plecs")

# 方法 2：手动在 PLECS 中打开模型后再运行脚本
```

---

### ❌ 错误：找不到 CSV 文件

**问题描述**：
```
[WARN] 未找到 sim_data.csv，跳过本轮文件采集
```

**排查步骤**：
1. **检查 PLECS Scope 配置**：
   - 双击模型中的 Scope 组件
   - 确认 "Log to file" 已勾选
   - 确认文件名为 `sim_data.csv`
   - 确认路径在 `CSV_SOURCE_CANDIDATES` 中

2. **查看仿真是否实际运行**：
   - 检查 PLECS 窗口是否显示仿真进度
   - 确认仿真时间足够长（至少几个周期）

3. **手动运行测试**：
   - 在 PLECS 中手动点击 "Run" 按钮
   - 确认 CSV 文件确实生成

**临时解决方案**：
```python
# 添加更多候选路径
CSV_SOURCE_CANDIDATES = [
    PROJECT_ROOT / "sim_data.csv",
    PROJECT_ROOT.parent / "sim_data.csv",
    pathlib.Path("C:/Users/YourName/Documents/PLECS/sim_data.csv"),
]
```

---

### ❌ 错误：参数未生效 / Parameters not applied

**问题描述**：所有仿真结果相同，参数扫描似乎无效。

**检查清单**：
1. **PLECS 模型中变量名称必须完全匹配**：
   ```python
   # 脚本中：
   SCAN_PARAMETERS = {"Udc": [350, 400, 450]}
   
   # PLECS 模型中：参数块的 Name 必须为 "Udc"（大小写敏感）
   ```

2. **变量作用域**：确保参数定义在模型的顶层（Model Variables），而非子系统局部变量

3. **参数类型**：PLECS 仅支持数值类型，不支持字符串或结构体

4. **调试方法**：在 PLECS 中添加 Display 组件显示参数值，确认是否更新

---

### ⚠️ 性能优化

**问题**：81 组仿真耗时过长（如每次仿真 30 秒，总计 40 分钟）

**优化建议**：

1. **减少仿真时间**：
   ```python
   # 在 optStruct 中添加
   opt_struct = {
       "ModelVars": params,
       "TimeSpan": [0, 0.1],  # 仅仿真 100ms
   }
   ```

2. **减少采样点数**：在 PLECS Scope 中设置更大的采样间隔

3. **并行仿真**（高级）：修改脚本支持多进程（需要多个 PLECS 许可证）

4. **GPU 加速**：使用 PLECS RT Box 进行实时仿真

---

### 🔬 高级：集成机器学习模型

**使用场景**：基于采集的数据训练 LSTM 模型预测 IGBT 结温。

**示例工作流**：
```bash
# 1. 数据采集（本工具）
python src/plecs_data_catcher.py

# 2. 数据预处理（用户自定义脚本）
python scripts/preprocess_data.py

# 3. 模型训练（用户自定义）
python scripts/train_lstm.py

# 4. 模型部署
# 将 igbt_lstm_model.pt 复制到目标系统
```

**加载已训练模型**：
```python
import torch

# 加载模型
model = torch.load("outputs/igbt_lstm_model.pt")
model.eval()

# 预测
import numpy as np
input_data = np.array([[350, 15000, 25]])  # [Udc, f_sw, T_amb]
prediction = model(torch.tensor(input_data, dtype=torch.float32))
print(f"预测结温: {prediction.item():.2f} °C")
```

---

## 📚 参考资料

- [PLECS 官方文档](https://www.plexim.com/download/documentation)
- [PLECS XML-RPC API](ref/xmlrpc_controller_design.pdf)
- [Python xmlrpc.client 文档](https://docs.python.org/3/library/xmlrpc.client.html)
- [PyTorch 官方教程](https://pytorch.org/tutorials/)

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

**开发建议**：
- 遵循 PEP 8 代码风格
- 添加类型注解（`from __future__ import annotations`）
- 提交前运行 `ruff check src/` 检查代码质量

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

---

## 🌟 致谢

- **[PLECS](https://www.plexim.com/)** - 专业的电力电子仿真软件
- **Python 社区** - 提供强大的标准库和生态系统
- **所有贡献者** - 感谢您的支持与反馈

---

## 📧 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 邮件：[您的邮箱]

---

**最后更新**：2026-03-09print(f"平均功率: {avg_power:.2f} W")

# 绘制结温曲线
import matplotlib.pyplot as plt
plt.plot(df['Time'], df['Tj_IGBT'])
plt.xlabel('时间 (s)')
plt.ylabel('结温 (°C)')
plt.show()
```

---

## 🔧 工作原理

### 核心流程图

```
┌─────────────────┐
│  启动脚本       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 连接 PLECS      │ ◄─── XML-RPC (http://127.0.0.1:1080)
│ XML-RPC Server  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 加载 .plecs 模型│ ◄─── plecs.load("model_name")
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 生成参数网格    │ ◄─── SCAN_PARAMETERS 笛卡尔积
│ (81 组参数)     │
└────────┬────────┘
         │
         ▼
    ┏━━━━┷━━━━┓
    ┃ for 循环  ┃
    ┗━━━━┯━━━━┛
         │
         ├─────────────────────┐
         │                     │
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ 设置参数        │   │ 运行仿真        │
│ (ModelVars)     │   │ plecs.simulate()│
└────────┬────────┘   └────────┬────────┘
         │                     │
         └──────────┬──────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ 等待仿真完成    │
           │ 查找 CSV 文件   │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ 复制并重命名    │
           │ 到 outputs/     │
           └────────┬────────┘
                    │
                    ▼
              [下一组参数]
                    │
                    ▼
           ┌─────────────────┐
           │ 全部完成        │
           │ 生成报告        │
           └─────────────────┘
```

### 技术细节

1. **连接管理**：使用 `xmlrpc.client.ServerProxy` 与 PLECS 通信
2. **参数传递**：通过 `optStruct.ModelVars` 字典注入模型参数
3. **错误处理**：自动尝试多种 API 候选方法（兼容不同 PLECS 版本）
4. **文件管理**：基于时间戳查找最新生成的 CSV 文件
5. **命名规范**：使用正则表达式清理参数值，确保文件名合法

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


