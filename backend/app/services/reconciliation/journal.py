import json
import os
from datetime import datetime
from typing import Dict, List

JOURNAL_PATH = os.getenv("TRIPLET_DELTA_JOURNAL", "/tmp/triplet_delta_journal.jsonl")


def journal_conflict(conflict_record: Dict):
    with open(JOURNAL_PATH, "a") as f:
        f.write(
            json.dumps({"timestamp": datetime.utcnow().isoformat(), **conflict_record})
            + "\n"
        )


def load_journal() -> List[Dict]:
    if not os.path.exists(JOURNAL_PATH):
        return []
    with open(JOURNAL_PATH) as f:
        return [json.loads(line) for line in f]
