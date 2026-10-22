"""Clone missing independent variants without overwriting existing directories."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ("local", "hybrid", "multicloud")


def main():
    for variant in VARIANTS:
        target = ROOT / variant
        origin = f"https://github.com/yhs0728/secure-doc-agent-{variant}.git"
        if target.exists():
            top = subprocess.check_output(
                ["git", "-C", str(target), "rev-parse", "--show-toplevel"], text=True
            ).strip()
            if Path(top).resolve() != target.resolve():
                raise RuntimeError(f"Not an independent repository: {target}")
            actual = subprocess.check_output(
                ["git", "-C", str(target), "remote", "get-url", "origin"], text=True
            ).strip()
            if actual != origin:
                raise RuntimeError(f"Unexpected origin for {target}")
            print(f"Already present: {target}")
        else:
            subprocess.run(["git", "clone", origin, str(target)], check=True)


if __name__ == "__main__":
    main()
