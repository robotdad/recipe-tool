#!/usr/bin/env python3
"""
Runs git-collector → falls back to npx automatically (with --yes) →
shows guidance only if everything fails.
"""

from shutil import which
import subprocess
import sys
from textwrap import dedent

OUTPUT_DIR = "ai_context/git_collector"


def guidance() -> str:
    return dedent(
        """\
        ❌  git-collector could not be run.

        Fixes:
          • Global install ……  npm i -g git-collector
          • Or rely on npx (no install).

        Then re-run:  make ai-context-files
        """
    )


def run(cmd: list[str], capture: bool = True) -> subprocess.CompletedProcess:
    """Run a command, optionally capturing its output."""
    print("→", " ".join(cmd))
    return subprocess.run(
        cmd,
        text=True,
        capture_output=capture,
    )


def main() -> None:
    root = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_DIR

    # Preferred runners in order
    runners: list[list[str]] = []
    if which("git-collector"):
        runners.append(["git-collector"])

    if which("pnpm"):
        try:
            # Check if git-collector is available via pnpm by running a simple list command
            # Redirect output to avoid cluttering the console
            result = subprocess.run(
                ["pnpm", "list", "git-collector"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )

            # If git-collector is in the output, it's installed via pnpm
            if "git-collector" in result.stdout and "ERR" not in result.stdout:
                 runners.append(["pnpm", "exec", "git-collector"])
        except Exception:
            # If any error occurs during check, move to next option
            pass

    if which("npx"):
        # --yes suppresses the “Need to install?” prompt :contentReference[oaicite:0]{index=0}
        runners.append(["npx", "--yes", "git-collector"])


    if not runners:
        sys.exit(guidance())

    last_result = None
    for r in runners:
        # Capture output for git-collector / pnpm, but stream for npx (shows progress)
        capture = r[0] != "npx" and r[0] != "git-collector"
        last_result = run(r + [root, "--update"], capture=capture)
        if last_result.returncode == 0:
            return  # success 🎉
        if r[:2] == ["pnpm", "exec"]:
            print("pnpm run not supported — falling back to npx …")

    # All attempts failed → print stderr (if any) and guidance
    if last_result and last_result.stderr:
        print(last_result.stderr.strip(), file=sys.stderr)
    sys.exit(guidance())


if __name__ == "__main__":
    main()
