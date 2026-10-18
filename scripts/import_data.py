"""Import một bộ data v3 vào DB (thay thế toàn bộ catalog) và tùy chọn tính embedding.

    python scripts/import_data.py --dataset cleaned_data/demo_v3 --embed
    python scripts/import_data.py --embed-only        # chỉ embed chunk còn thiếu

--embed cần OPENROUTER_API_KEY. Không embed thì tìm kiếm tài liệu dùng BM25.
Nhớ đặt DATASET_DIR trong .env trùng với bộ vừa import, nếu không server sẽ import lại bộ cũ khi khởi động.
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dataset.importer import DatasetValidationError, embed_missing_chunks, import_dataset  # noqa: E402
from src.dataset.loader import load_dataset  # noqa: E402
from src.db.session import get_session_factory, init_database  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dataset", default="cleaned_data/demo_v3")
    parser.add_argument("--embed", action="store_true", help="tính embedding cho knowledge chunks sau khi import")
    parser.add_argument("--embed-only", action="store_true", help="không import, chỉ embed chunk còn thiếu")
    args = parser.parse_args()

    init_database()
    with get_session_factory()() as session:
        if not args.embed_only:
            try:
                version = import_dataset(session, load_dataset(args.dataset))
            except DatasetValidationError as exc:
                print(exc)
                print("\nChạy scripts/validate_data.py để xem đầy đủ.")
                return 1
            print(f"Đã import {version.version} (demo={version.is_demo}): {version.counts}")
        if args.embed or args.embed_only:
            count = asyncio.run(embed_missing_chunks(session))
            print(f"Đã embed {count} chunk")
    return 0


if __name__ == "__main__":
    sys.exit(main())
