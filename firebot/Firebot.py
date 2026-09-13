import json
import subprocess
import sys
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
WORKSPACE = SELF_PATH.parent
CLONES_DIR = WORKSPACE / "clones"
MAX_VARIANTS = 4
LEARNING_LOG = CLONES_DIR / "learning_log.jsonl"


def build_variant(seed: int, score: int) -> str:
    template = SELF_PATH.read_text(encoding="utf-8")
    delta = seed + score
    template = template.replace("SEED = 1", f"SEED = {seed}")
    template = template.replace("SCORE = 0", f"SCORE = {score}")
    template = template.replace("DELTA = 1", f"DELTA = {delta}")
    return template


def evaluate_variant(path: Path) -> int:
    result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
    return result.returncode


def spawn_and_run() -> None:
    CLONES_DIR.mkdir(exist_ok=True, parents=True)
    reward = 0
    observed = []

    for index in range(1, MAX_VARIANTS + 1):
        candidate = CLONES_DIR / f"candidate_{index}.py"
        candidate.write_text(build_variant(index, reward), encoding="utf-8")

        exit_code = evaluate_variant(candidate)
        event = {
            "variant": index,
            "reward": reward,
            "exit_code": exit_code,
            "success": exit_code == 0,
        }
        observed.append(event)
        with LEARNING_LOG.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")

        if exit_code == 0:
            reward += 1
        else:
            reward = max(0, reward - 1)
            candidate.unlink(missing_ok=True)

    best = max(observed, key=lambda item: (item["success"], item["reward"]), default={"success": False, "reward": 0})
    return best


if __name__ == "__main__":
    result = spawn_and_run()
    print(json.dumps(result, sort_keys=True))
