"""
PLECS 批量仿真与数据提取工具

功能：
  1. 参数扫描：遍历多个参数组合
  2. 自动仿真：调用 PLECS.simulate()
  3. CSV 采集：采集 PLECS 模型生成的 CSV 数据

使用：
  python src/plecs_data_catcher.py
"""

from __future__ import annotations

import pathlib
import re
import shutil
import xmlrpc.client
from typing import Any
import itertools


# ============================================================================
# 配置区
# ============================================================================

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
PLECS_URL = "http://127.0.0.1:1080/RPC2"
MODEL_FILE = PROJECT_ROOT / "py_grid_connected_convert.plecs"
if not MODEL_FILE.exists():
	fallback_model = PROJECT_ROOT.parent / "py_grid_connected_convert.plecs"
	if fallback_model.exists():
		MODEL_FILE = fallback_model
OUTPUT_DIR = PROJECT_ROOT / "outputs"
CSV_OUTPUT_FILE = OUTPUT_DIR / "sim_data.csv"

# 参数扫描范围
SCAN_PARAMETERS = {
    "Udc": [350, 400, 450],              # DC 总线电压 (V)
    "f_sw": [15000, 18000, 21000],      # 开关频率 (Hz)
	#"R": [8, 10, 12],                    # 电网侧电阻 (Ohm)
	"environ_T": [25, 40, 55],           # 环境温度 (degC)
}

# 寻找 CSV 的候选位置
CSV_SOURCE_CANDIDATES = [
	PROJECT_ROOT / "sim_data.csv",
	PROJECT_ROOT.parent / "sim_data.csv",
]

# ============================================================================
# 工具函数
# ============================================================================

def ensure_output_dir() -> None:
	"""创建输出目录，并清空旧文件。"""
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
	# 清空目录中的 CSV 文件
	for csv_file in OUTPUT_DIR.glob("sim_data_*.csv"):
		csv_file.unlink()
		print(f"[INFO] 已删除旧文件: {csv_file.name}")
	print(f"[INFO] 输出目录: {OUTPUT_DIR.resolve()}")


def list_methods(proxy: xmlrpc.client.ServerProxy) -> list[str]:
	"""获取 XML-RPC 暴露的方法列表。"""
	methods = proxy.system.listMethods()
	if not isinstance(methods, list):
		raise RuntimeError(f"system.listMethods 返回异常类型: {type(methods)}")
	return [str(m) for m in methods]


def call_method(proxy: xmlrpc.client.ServerProxy, method_name: str, *args: Any) -> Any:
	"""按方法名动态调用 XML-RPC 接口。"""
	method: Any = proxy
	for part in method_name.split("."):
		method = getattr(method, part)
	return method(*args)


def try_first_available(
	proxy: xmlrpc.client.ServerProxy,
	candidates: list[str],
	*args: Any,
) -> tuple[str, Any]:
	"""从候选方法名中依次尝试，返回第一个成功调用的方法及结果。"""
	last_error: Exception | None = None
	for name in candidates:
		try:
			return name, call_method(proxy, name, *args)
		except Exception as e:
			last_error = e

	raise RuntimeError(
		f"候选方法都不可用: {candidates}; 最后一次错误: {last_error}"
	)


def call_with_signatures(
	proxy: xmlrpc.client.ServerProxy,
	method_candidates: list[str],
	args_candidates: list[tuple[Any, ...]],
) -> tuple[str, Any]:
	"""按“方法名 × 参数签名”组合尝试调用，返回第一个成功结果。"""
	last_error: Exception | None = None
	for method in method_candidates:
		for args in args_candidates:
			try:
				return method, call_method(proxy, method, *args)
			except Exception as e:
				last_error = e

	raise RuntimeError(
		f"调用失败，方法候选={method_candidates}，最后错误={last_error}"
	)


def build_param_grid(scan_parameters: dict[str, list[Any]]) -> list[dict[str, Any]]:
	"""生成参数组合网格。"""
	if not scan_parameters:
		return [{}]
	keys = list(scan_parameters.keys())
	values = [scan_parameters[k] for k in keys]
	return [dict(zip(keys, combo)) for combo in itertools.product(*values)]


def build_opt_struct(params: dict[str, Any]) -> dict[str, Any]:
	"""构建 PLECS optStruct，包含 ModelVars 字段。"""
	return {
		"ModelVars": params
	}


def run_simulation_once(proxy: xmlrpc.client.ServerProxy, params: dict[str, Any]) -> bool:
	"""执行一次仿真，参数通过 optStruct 传递。"""
	opt_struct = build_opt_struct(params)
	# 使用模型名称（不带路径和扩展名）
	model_name = MODEL_FILE.stem
	try:
		result = call_method(proxy, "plecs.simulate", model_name, opt_struct)
		print(f"[OK] 仿真完成，返回: {result}")
		return True
	except Exception as e:
		print(f"[WARN] 仿真调用失败: {e}")
		return False


def find_latest_csv() -> pathlib.Path | None:
	"""从候选位置查找最新的 sim_data.csv。"""
	existing = [p for p in CSV_SOURCE_CANDIDATES if p.exists()]
	if not existing:
		return None
	return max(existing, key=lambda p: p.stat().st_mtime)


def sanitize_tag(value: Any) -> str:
	"""将值转换为可用于文件名的安全片段。"""
	text = str(value)
	text = re.sub(r"[^0-9A-Za-z_.-]+", "_", text)
	return text.strip("_") or "na"


def make_run_file_name(run_idx: int, params: dict[str, Any]) -> str:
	"""构造每次仿真的 CSV 文件名。"""
	parts = [f"run_{run_idx:03d}"]
	for key in sorted(params.keys()):
		parts.append(f"{key}_{sanitize_tag(params[key])}")
	return "sim_data_" + "__".join(parts) + ".csv"


def copy_csv_for_run(run_idx: int, params: dict[str, Any]) -> pathlib.Path | None:
	"""复制最新 CSV 到 outputs，并生成带参数信息的文件名。"""
	source = find_latest_csv()
	if source is None:
		print("[WARN] 未找到 sim_data.csv，跳过本轮文件采集")
		return None

	target_name = make_run_file_name(run_idx, params)
	target = OUTPUT_DIR / target_name
	shutil.copy2(source, target)
	print(f"[OK] 采集 CSV: {target}")

	# 维护一个“最新 CSV”软标准副本，便于外部工具读取
	shutil.copy2(source, CSV_OUTPUT_FILE)
	return target


def run_param_sweep(proxy: xmlrpc.client.ServerProxy) -> int:
	"""执行参数扫描、仿真和原始 CSV 数据采集。"""
	param_grid = build_param_grid(SCAN_PARAMETERS)
	print(f"[INFO] 参数组合数: {len(param_grid)}")

	collected_count = 0
	for idx, params in enumerate(param_grid, start=1):
		print(f"\n[INFO] ===== Run {idx}/{len(param_grid)} =====")
		print(f"[INFO] 参数: {params}")

		sim_ok = run_simulation_once(proxy, params)
		if sim_ok:
			csv_path = copy_csv_for_run(idx, params)
			if csv_path is not None:
				collected_count += 1
		else:
			print(f"[WARN] 本轮仿真失败，跳过数据采集")

	print(f"\n[INFO] 原始 CSV 采集完成: {collected_count}/{len(param_grid)}")

	return 0


def connect_plecs() -> tuple[xmlrpc.client.ServerProxy | None, list[str]]:
	"""连接到 PLECS XML-RPC 服务。"""
	print(f"[INFO] 连接到 PLECS XML-RPC: {PLECS_URL}")
	proxy = xmlrpc.client.ServerProxy(PLECS_URL, allow_none=True, use_builtin_types=True)

	try:
		methods = list_methods(proxy)
	except Exception as e:
		print("[ERROR] 无法连接到 PLECS XML-RPC 服务。")
		print(f"        详情: {e}")
		print("[HINT] 请确认：")
		print("       - PLECS 已启动")
		print("       - XML-RPC 已启用")
		print("       - Host/Port 与本脚本一致")
		return None, []

	print(f"[OK] 已连接，方法数量: {len(methods)}")
	print("[INFO] 前 30 个方法:")
	for m in methods[:30]:
		print("   -", m)

	# 可选：查看某个方法签名/帮助（如果服务支持）
	if "system.methodHelp" in methods and methods:
		target = methods[0]
		try:
			help_text = call_method(proxy, "system.methodHelp", target)
			print(f"[INFO] methodHelp({target}):")
			print(help_text)
		except Exception:
			pass

	# 加载模型
	try:
		method_name, result = try_first_available(
			proxy,
			["plecs.load", "Load", "load"],
			str(MODEL_FILE),
		)
		print(f"[OK] 已调用 {method_name}，返回: {result}")
	except Exception as e:
		print("[WARN] 未执行模型加载。")
		print(f"       详情: {e}")

	return proxy, methods


def main() -> int:
	"""脚本入口。"""
	ensure_output_dir()
	if not MODEL_FILE.exists():
		print(f"[WARN] 未找到模型文件: {MODEL_FILE}")
		print("[HINT] 请将 .plecs 模型放在项目根目录，或修改 MODEL_FILE 路径")
	proxy, _ = connect_plecs()
	if proxy is None:
		return 1

	code = run_param_sweep(proxy)

	print("\n[INFO] 输出文件汇总:")
	for p in sorted(OUTPUT_DIR.glob("*")):
		if p.is_file():
			print(f"  - {p}")

	return code


if __name__ == "__main__":
	raise SystemExit(main())
