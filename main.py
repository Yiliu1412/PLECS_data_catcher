from __future__ import annotations

from pathlib import Path

from src.plecs_data_catcher import connect_plecs, ensure_output_dir, run_param_sweep
from src.plecs_visualizer import OUTPUT_DIR, plot_single_file

# ============================================================================
# 配置区
# ============================================================================

SCAN_PARAMETERS = {
    "Udc": [200, 300, 400],
    "f_sw": [10000, 16000, 18000, 20000],
    "environ_T": [25, 40, 60],
    "Igd_ref": [30, 40, 50, 60],
}

TEMP_COLUMN = "IGBT1:IGBT junction temp"
PLOT_TIME_RANGE = (0, 5)


# ============================================================================
# 回调函数
# ============================================================================

def plot_after_collect(csv_path: Path, run_idx: int, _params: dict[str, object]) -> None:
    """每次采集到 CSV 后立即绘图。"""
    save_path = csv_path.with_suffix(".png")
    title = f"IGBT Junction Temperature - Run {run_idx:03d}"
    print(f"[INFO] 开始绘图: {csv_path.name}")
    plot_single_file(
        csv_path,
        time_range=PLOT_TIME_RANGE,
        temp_column=TEMP_COLUMN,
        title=title,
        save_path=save_path,
    )


# ============================================================================
# 主函数
# ============================================================================

def main() -> int:
    ensure_output_dir()
    proxy, _ = connect_plecs()
    if proxy is None:
        return 1

    return run_param_sweep(
        proxy,
        scan_parameters=SCAN_PARAMETERS,
        on_csv_collected=plot_after_collect,
    )


if __name__ == "__main__":
    raise SystemExit(main())
