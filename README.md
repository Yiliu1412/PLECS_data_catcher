# PLECS Data Catcher

🔌 PLECS 电力电子仿真参数扫描与数据自动采集工具（基于 XML-RPC）

## 项目简介

自动化 PLECS 仿真的 Python 工具，支持多维参数扫描、工程数据采集和结果管理。

**核心功能**
- 批量参数扫描（电压、频率、温度等多维空间）
- 通过 XML-RPC 自动调用 PLECS 仿真引擎
- 自动采集并重命名 CSV 数据
- 为每组参数生成独立数据文件

## 快速开始

### 1. 环境要求

| 组件 | 版本 |
|------|------|
| Python | 3.10+ |
| PLECS | 4.0+ |

> 数据采集脚本只需 Python 标准库，无需第三方包。`requirements.txt` 用于可选的数据分析功能。

### 2. 安装

```bash
git clone <repository-url>
cd PLCES_data_catcher

# 创建虚拟环境（推荐）
python -m venv .venv
.venv\Scripts\activate  # Windows

# 仅运行采集脚本（无需额外依赖）
python src/plecs_data_catcher.py

# 完整功能（数据分析）
pip install -r requirements.txt
```

---

### 3. 配置 PLECS XML-RPC Server

在运行脚本前，必须启动 PLECS 的 XML-RPC 服务

### 4. 配置 To file 模块

在 PLECS 中使用 To File模块选择您需要的数据输出。

#### 5. 验证连接
运行以下 Python 代码测试连接：
```python
import xmlrpc.client
proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:1080/RPC2")
print(proxy.system.listMethods())
```

## 使用方法

### 基本用法

```bash
python src/plecs_data_catcher.py
```

### 配置参数扫描

编辑 [src/plecs_data_catcher.py](src/plecs_data_catcher.py) 中的参数配置：

```python
SCAN_PARAMETERS = {
    "Udc": [350, 400, 450],              # DC 母线电压 (V)
    "f_sw": [15000, 18000, 21000],      # 开关频率 (Hz)
    "environ_T": [25, 40, 55],           # 环境温度 (°C)
}
```

**自动调整模型文件路径**：
```python
MODEL_FILE = PROJECT_ROOT / "your_model.plecs"
```

## 项目结构

```
PLCES_data_catcher/
├── src/plecs_data_catcher.py      # 主脚本
├── outputs/                        # 输出数据目录
│   ├── sim_data_run_*.csv         # 仿真结果
│   └── sim_data.csv               # 最新数据副本
├── ref/                           # 参考文档
├── requirements.txt               # Python 依赖
├── README.md                      # 本文件
└── LICENSE
```

## 输出文件格式

CSV 文件命名规则：`sim_data_run_{序号}__{参数1}_{值1}__{参数2}_{值2}__.csv`

示例：
- `sim_data_run_001__Udc_350__environ_T_25__f_sw_15000.csv`
- `sim_data_run_027__Udc_450__environ_T_55__f_sw_21000.csv`


## 参考资源

- [PLECS 官方文档](https://www.plexim.com/download/documentation)
- [Python xmlrpc 文档](https://docs.python.org/3/library/xmlrpc.client.html)


## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

## 🌟 致谢

- **[PLECS](https://www.plexim.com/)** - 专业的电力电子仿真软件
- **Python 社区** - 提供强大的标准库和生态系统
- **所有贡献者** - 感谢您的支持与反馈
