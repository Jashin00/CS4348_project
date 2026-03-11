#!/usr/bin/env python3

import sys
from datetime import datetime


def format_log_line(message: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    stripped = message.strip()
    if not stripped:
        action = "INFO"
        rest = ""
    else:
        parts = stripped.split(maxsplit=1)
        action = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

    if rest:
        return f"{timestamp} [{action}] {rest}"
    return f"{timestamp} [{action}]"


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 logger.py <logfile>", file=sys.stderr)
        sys.exit(1)

    log_filename = sys.argv[1]

    try:
        with open(log_filename, "a", encoding="utf-8") as log_file:
            for line in sys.stdin:
                msg = line.rstrip("\n")
                if msg == "QUIT":
                    break

                formatted = format_log_line(msg)
                log_file.write(formatted + "\n")
                log_file.flush()

    except OSError as e:
        print(f"Logger file error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()