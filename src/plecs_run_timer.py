"""
PLECS 仿真运行计时记录器。

功能：
  1. 为一组仿真生成一个汇总 CSV
  2. 按次追加扫描参数、运行时间和状态
  3. CSV 文件名自动使用模型名 + 时间戳
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import csv
import pathlib
from typing import Any


@dataclass
class RunTimingRecorder:
	"""按次记录仿真耗时到单个 CSV 文件。"""

	output_dir: pathlib.Path
	model_name: str
	parameter_names: list[str]
	file_path: pathlib.Path = field(init=False)
	fieldnames: list[str] = field(init=False)

	def __post_init__(self) -> None:
		self.output_dir.mkdir(parents=True, exist_ok=True)
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
		self.file_path = self.output_dir / f"{self.model_name}_{timestamp}.csv"
		self.fieldnames = ["run序号", *self.parameter_names, "运行时间", "是否成功"]
		with open(self.file_path, "w", newline="", encoding="utf-8-sig") as file_handle:
			writer = csv.DictWriter(file_handle, fieldnames=self.fieldnames)
			writer.writeheader()

	def record(self, run_idx: int, params: dict[str, Any], elapsed_seconds: float, success: bool) -> None:
		"""追加一行运行记录。"""
		row = {
			"run序号": run_idx,
			"运行时间": f"{elapsed_seconds:.6f}",
			"是否成功": "是" if success else "否",
		}
		for name in self.parameter_names:
			row[name] = params.get(name, "")

		with open(self.file_path, "a", newline="", encoding="utf-8-sig") as file_handle:
			writer = csv.DictWriter(file_handle, fieldnames=self.fieldnames)
			writer.writerow(row)

		print(f"[OK] 已写入计时记录: {self.file_path.name}")
