"""Dispatch Compose to one independent checkout, optionally through Ubuntu WSL."""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def command(variant, arguments, wsl=False):
    target = ROOT / variant / "tools" / "compose.py"
    if variant not in ("local", "hybrid", "multicloud") or not target.is_file():
        raise ValueError("Choose an installed local, hybrid, or multicloud repository")
    if wsl:
        path = target.resolve()
        if not path.drive:
            raise ValueError("--wsl requires a Windows checkout")
        linux_path = "/mnt/" + path.drive[0].lower() + "/" + "/".join(path.parts[1:])
        return ["wsl", "-d", "Ubuntu", "--exec", "python3", linux_path, *arguments]
    return [sys.executable, str(target), *arguments]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wsl", action="store_true")
    parser.add_argument("variant", choices=("local", "hybrid", "multicloud"))
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    return subprocess.call(command(args.variant, args.arguments, args.wsl))


if __name__ == "__main__":
    raise SystemExit(main())
