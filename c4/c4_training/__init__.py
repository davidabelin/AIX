"""Dataset ingestion helpers for c4 supervised training."""

from c4_training.dataset import (
    LegacyMoveRecord,
    import_legacy_file,
    infer_legacy_format,
    parse_jsonl_records,
    parse_semicolon_records,
    write_training_csv,
)

__all__ = [
    "LegacyMoveRecord",
    "infer_legacy_format",
    "parse_jsonl_records",
    "parse_semicolon_records",
    "write_training_csv",
    "import_legacy_file",
]
