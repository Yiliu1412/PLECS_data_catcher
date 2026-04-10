"""
PLECS 仿真数据可视化工具

功能：
    1. 加载仿真生成的 CSV 数据
    2. 绘制关键参数（如结温）随时间变化的曲线
    3. 支持按文件选择单次运行结果
    4. 灵活的绘图配置和接口

使用：
  python src/plecs_visualizer.py
"""

import pathlib
from typing import Optional, Dict, List, Tuple
import argparse
import csv
import matplotlib.pyplot as plt
import matplotlib
from dataclasses import dataclass

# 设置 matplotlib 后端（非交互式，适合服务器环境）
matplotlib.use('Agg')

# ============================================================================
# 配置区
# ============================================================================

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# 绘图配置
PLOT_CONFIG = {
    "figsize": (12, 6),
    "dpi": 100,
    "style": "seaborn-v0_8-darkgrid",  # 绘图风格
}

# 时间范围配置（单位：秒）
TIME_RANGE = (0, 5)

# 结温列名（从 CSV 中查找）
TEMPERATURE_COLUMN_NAMES = [
    "IGBT1:IGBT junction temp",
]

# ============================================================================
# 数据类
# ============================================================================

@dataclass
class CSVData:
    """CSV 数据容器"""
    time: List[float]
    temperature: List[float]
    filename: str
    metadata: Dict = None


# ============================================================================
# 核心函数
# ============================================================================

def load_csv_data(csv_file: pathlib.Path, temp_column: Optional[str] = None) -> CSVData:
    """
    加载 CSV 文件并提取时间和温度数据。
    
    Args:
        csv_file: CSV 文件路径
        temp_column: 温度列名（如不指定，则自动搜索）
    
    Returns:
        CSVData 对象
    """
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV 文件不存在: {csv_file}")
    
    time_data = []
    temp_data = []
    column_index = None
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        # 自动查找温度列
        if temp_column is None:
            for candidate in TEMPERATURE_COLUMN_NAMES:
                if candidate in headers:
                    temp_column = candidate
                    break
        
        if temp_column is None:
            raise ValueError(
                f"未找到温度列。可用列: {headers}\n"
                f"请在 TEMPERATURE_COLUMN_NAMES 中添加列名或指定 temp_column 参数。"
            )
        
        column_index = headers.index(temp_column)
        time_index = headers.index("Time")
        
        # 读取数据
        for row in reader:
            try:
                time_data.append(float(row[time_index]))
                temp_data.append(float(row[column_index]))
            except (ValueError, IndexError) as e:
                print(f"[WARN] 跳过无效行: {row} ({e})")
    
    metadata = {
        "temp_column": temp_column,
        "num_samples": len(time_data),
        "time_range": (min(time_data) if time_data else 0, max(time_data) if time_data else 0),
        "temp_range": (min(temp_data) if temp_data else 0, max(temp_data) if temp_data else 0),
    }
    
    return CSVData(
        time=time_data,
        temperature=temp_data,
        filename=csv_file.name,
        metadata=metadata
    )


def plot_single_file(
    csv_file: pathlib.Path,
    time_range: Tuple[float, float] = TIME_RANGE,
    temp_column: Optional[str] = None,
    title: Optional[str] = None,
    ylabel: str = "Junction Temperature (°C)",
    save_path: Optional[pathlib.Path] = None,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    绘制单个 CSV 文件的结温曲线。
    
    Args:
        csv_file: CSV 文件路径
        time_range: 时间范围 (min, max)
        temp_column: 温度列名
        title: 图表标题
        ylabel: Y 轴标签
        save_path: 保存图表的路径（不指定则不保存）
    
    Returns:
        (图表对象, 轴对象)
    """
    data = load_csv_data(csv_file, temp_column=temp_column)
    
    # 应用时间范围过滤
    filtered_indices = [i for i, t in enumerate(data.time) if time_range[0] <= t <= time_range[1]]
    time_filtered = [data.time[i] for i in filtered_indices]
    temp_filtered = [data.temperature[i] for i in filtered_indices]
    
    # 创建图表
    plt.style.use(PLOT_CONFIG["style"])
    fig, ax = plt.subplots(figsize=PLOT_CONFIG["figsize"], dpi=PLOT_CONFIG["dpi"])
    
    # 绘制曲线
    ax.plot(time_filtered, temp_filtered, linewidth=2, marker='o', markersize=3, label=data.filename)
    
    # 设置标题和标签
    if title is None:
        title = f"IGBT Junction Temperature - {data.filename}"
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel("Time (s)", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    
    # 设置时间轴范围
    ax.set_xlim(time_range)
    
    # 网格和图例
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    # 显示数据统计信息
    temp_min = min(temp_filtered) if temp_filtered else 0
    temp_max = max(temp_filtered) if temp_filtered else 0
    temp_avg = sum(temp_filtered) / len(temp_filtered) if temp_filtered else 0
    
    stats_text = (
        f"Samples: {len(temp_filtered)}\n"
        f"Min: {temp_min:.2f}°C\n"
        f"Max: {temp_max:.2f}°C\n"
        f"Avg: {temp_avg:.2f}°C"
    )
    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    fig.tight_layout()
    
    # 保存图表
    if save_path is not None:
        fig.savefig(save_path, dpi=PLOT_CONFIG["dpi"], bbox_inches='tight')
        print(f"[INFO] 图表已保存: {save_path}")
    
    return fig, ax


def plot_multiple_files(
    csv_files: List[pathlib.Path],
    time_range: Tuple[float, float] = TIME_RANGE,
    temp_column: Optional[str] = None,
    title: str = "IGBT Junction Temperature Comparison",
    ylabel: str = "Junction Temperature (°C)",
    save_path: Optional[pathlib.Path] = None,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    绘制多个 CSV 文件的结温曲线对比。
    
    Args:
        csv_files: CSV 文件路径列表
        time_range: 时间范围 (min, max)
        temp_column: 温度列名
        title: 图表标题
        ylabel: Y 轴标签
        save_path: 保存图表的路径（不指定则不保存）
    
    Returns:
        (图表对象, 轴对象)
    """
    plt.style.use(PLOT_CONFIG["style"])
    fig, ax = plt.subplots(figsize=PLOT_CONFIG["figsize"], dpi=PLOT_CONFIG["dpi"])
    
    all_temps = []
    for csv_file in csv_files:
        data = load_csv_data(csv_file, temp_column=temp_column)
        
        # 应用时间范围过滤
        filtered_indices = [i for i, t in enumerate(data.time) if time_range[0] <= t <= time_range[1]]
        time_filtered = [data.time[i] for i in filtered_indices]
        temp_filtered = [data.temperature[i] for i in filtered_indices]
        
        all_temps.extend(temp_filtered)
        
        # 绘制曲线
        ax.plot(time_filtered, temp_filtered, linewidth=2, marker='o', markersize=2, 
                label=data.filename, alpha=0.8)
    
    # 设置标题和标签
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel("Time (s)", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    
    # 设置时间轴范围
    ax.set_xlim(time_range)
    
    # 网格和图例
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, loc='best')
    
    fig.tight_layout()
    
    # 保存图表
    if save_path is not None:
        fig.savefig(save_path, dpi=PLOT_CONFIG["dpi"], bbox_inches='tight')
        print(f"[INFO] 图表已保存: {save_path}")
    
    return fig, ax


def list_csv_files(output_dir: pathlib.Path = OUTPUT_DIR) -> List[pathlib.Path]:
    """
    列出输出目录中的所有 CSV 文件。
    
    Args:
        output_dir: 输出目录路径
    
    Returns:
        CSV 文件路径列表
    """
    if not output_dir.exists():
        print(f"[ERROR] 输出目录不存在: {output_dir}")
        return []
    
    csv_files = sorted(output_dir.glob("sim_data_run_*.csv"))
    print(f"[INFO] 找到 {len(csv_files)} 个 CSV 文件")
    for i, f in enumerate(csv_files[:5], 1):  # 显示前 5 个
        print(f"  {i}. {f.name}")
    if len(csv_files) > 5:
        print(f"  ... 共 {len(csv_files)} 个文件")
    
    return csv_files


def select_csv_file(csv_file: Optional[pathlib.Path] = None) -> pathlib.Path:
    """选择要绘制的 CSV 文件。未指定时默认使用最新的单次运行结果。"""
    if csv_file is not None:
        if not csv_file.exists():
            raise FileNotFoundError(f"指定的 CSV 文件不存在: {csv_file}")
        return csv_file

    csv_files = list_csv_files(OUTPUT_DIR)
    if not csv_files:
        raise FileNotFoundError("未找到可用的 CSV 数据文件。")

    return csv_files[0]


# ============================================================================
# 主函数
# ============================================================================

def main() -> None:
    """主函数：绘制单次运行结果。"""
    parser = argparse.ArgumentParser(description="PLECS 仿真数据可视化工具")
    parser.add_argument(
        "--csv-file",
        type=pathlib.Path,
        default=None,
        help="指定要绘制的 CSV 文件；不指定时默认取 outputs 中的第一个运行结果",
    )
    parser.add_argument(
        "--save-path",
        type=pathlib.Path,
        default=None,
        help="图表保存路径；不指定时默认与 CSV 同名，仅扩展名改为 .png",
    )
    args = parser.parse_args()

    print("[INFO] PLECS 仿真数据可视化工具")
    print(f"[INFO] 输出目录: {OUTPUT_DIR}")
    
    try:
        target_file = select_csv_file(args.csv_file)
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    print(f"[INFO] 选择文件: {target_file.name}")
    save_path = args.save_path if args.save_path is not None else target_file.with_suffix(".png")
    
    try:
        fig1, ax1 = plot_single_file(
            target_file,
            time_range=TIME_RANGE,
            save_path=save_path,
        )
        print("[OK] 单文件绘图完成")
    except Exception as e:
        print(f"[ERROR] 绘图失败: {e}")
        return
    
    print("\n[OK] 可视化完成！")


# ============================================================================
# 命令行接口
# ============================================================================

if __name__ == "__main__":
    main()
