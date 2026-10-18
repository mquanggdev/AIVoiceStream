"""Kiểm tra một bộ data theo docs/data_spec_v3.md (quy tắc V1–V11).

    python scripts/validate_data.py cleaned_data/v3
Thoát với mã 1 nếu có lỗi.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dataset.loader import load_dataset  # noqa: E402
from src.dataset.validate import validate_dataset  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dataset_dir", nargs="?", default="cleaned_data/demo_v3")
    args = parser.parse_args()

    ds = load_dataset(args.dataset_dir)
    report = validate_dataset(ds)
    print(f"Dataset: {ds.version} (demo={ds.is_demo}) tại {ds.root}")
    print(
        f"  {len(ds.subdivisions)} phân khu, {len(ds.buildings)} tòa, {len(ds.units)} căn, "
        f"{len(ds.sales_policies)} chính sách, {len(ds.knowledge_docs)} tài liệu"
    )
    for line in report.errors:
        print(f"LỖI     {line}")
    for line in report.warnings:
        print(f"CẢNH BÁO {line}")
    print(f"\n{len(report.errors)} lỗi, {len(report.warnings)} cảnh báo")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
