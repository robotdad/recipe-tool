#!/usr/bin/env python3
import subprocess
import sys

OUTPUT_DIR = "ai_context/git_collector"


def find_git_collector():
    from shutil import which

    # Check for git-collector in PATH
    if which("git-collector"):
        return ["git-collector"]
    # Try to use it via npm, pnpm, or npx
    if which("pnpm"):
        return ["pnpm", "exec", "git-collector"]
    if which("npx"):
        return ["npx", "git-collector"]
    return None


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DIR
    runner = find_git_collector()
    if not runner:
        sys.exit("❌ git-collector not found (try `npm install -g git-collector`, or use pnpm/npx).")
    cmd = runner + [root, "--update"]
    print("→", " ".join(cmd))
    subprocess.run(cmd, check=True)
