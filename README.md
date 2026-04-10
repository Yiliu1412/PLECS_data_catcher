# PLECS Data Catcher

🔌 PLECS 电力电子仿真参数扫描、数据自动采集、运行计时与逐次绘图工具（基于 XML-RPC）

## 项目简介

自动化 PLECS 仿真的 Python 工具，支持多维参数扫描、工程数据采集、运行时间统计、逐次结果绘图和文件管理。

**核心功能**
- 批量参数扫描（电压、频率、温度等多维空间）
- 通过 XML-RPC 自动调用 PLECS 仿真引擎
- 自动采集并重命名 CSV 数据
- 为每组参数生成独立数据文件
- 记录每次仿真的扫描参数、运行时间和成功状态
- 每次采集完成后立即绘制对应曲线图

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

# 运行主入口（采集 + 逐次绘图）
python main.py

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
python main.py
```

### 配置参数扫描

编辑 [main.py](main.py) 中的参数配置：

```python
SCAN_PARAMETERS = {
    "Udc": [200, 300, 400],
    "f_sw": [10000, 16000, 18000, 20000],
    "environ_T": [25, 40, 60],
    "Igd_ref": [30, 40, 50, 60],
}
```

### 输出清理行为

每次运行前，程序会先清空 [outputs](outputs) 目录下的所有旧文件和子目录，再开始新的仿真任务。

### 绘图行为

每次仿真完成并采集到 CSV 后，程序会立刻调用可视化脚本生成对应 PNG 图像。

- 输入 CSV：`outputs/sim_data_run_XXX__*.csv`
- 输出图片：与 CSV 同名，仅扩展名改为 `.png`
- 时间范围：默认只显示 `0 - 5 s`

如果需要单独绘图，也可以直接运行：

```bash
python src/plecs_visualizer.py --csv-file outputs/sim_data_run_001__Igd_ref_30__Udc_200__environ_T_25__f_sw_10000.csv
```

### 运行计时汇总

每轮仿真完成后，会将计时结果追加到一个汇总 CSV 中。该文件名采用“模型名 + 时间戳”的形式，例如：

```text
py_grid_connected_convert_20260410_153012_123456.csv
```

汇总 CSV 的列顺序如下：

- `run序号`
- 各扫描参数列
- `运行时间`
- `是否成功`

其中 `是否成功` 使用 `是` / `否` 表示本次仿真是否成功完成。

## 项目结构

```
PLCES_data_catcher/
├── main.py                       # 入口：配置参数、运行仿真、逐次绘图、计时汇总
├── src/plecs_data_catcher.py      # 采集与仿真接口
├── src/plecs_run_timer.py        # 运行时间记录模块
├── src/plecs_visualizer.py        # 单文件结温绘图脚本
├── outputs/                        # 输出数据目录
│   ├── sim_data_run_*.csv         # 仿真结果
│   ├── sim_data_run_*.png         # 对应图像
│   ├── *.csv                     # 运行计时汇总文件
│   └── sim_data.csv               # 最新数据副本
├── ref/                           # 参考文档
├── requirements.txt               # Python 依赖
├── README.md                      # 本文件
└── LICENSE
```

## 输出文件格式

CSV 文件命名规则：`sim_data_run_{序号}__{参数1}_{值1}__{参数2}_{值2}.csv`

示例：
- `sim_data_run_001__Udc_350__environ_T_25__f_sw_15000.csv`
- `sim_data_run_027__Udc_450__environ_T_55__f_sw_21000.csv`

图片文件命名规则：与 CSV 完全同名，只把后缀改为 `.png`

示例：
- `sim_data_run_001__Udc_350__environ_T_25__f_sw_15000.png`
- `sim_data_run_027__Udc_450__environ_T_55__f_sw_21000.png`

计时汇总文件命名规则：`{模型名}_{时间戳}.csv`

示例：
- `py_grid_connected_convert_20260410_153012_123456.csv`


## 参考资源

- [PLECS 官方文档](https://www.plexim.com/download/documentation)
- [Python xmlrpc 文档](https://docs.python.org/3/library/xmlrpc.client.html)


## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

## 🌟 致谢

- **[PLECS](https://www.plexim.com/)** - 专业的电力电子仿真软件
- **Python 社区** - 提供强大的标准库和生态系统
- **所有贡献者** - 感谢您的支持与反馈
