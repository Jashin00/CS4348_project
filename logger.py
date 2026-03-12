#!/usr/bin/env python3

import sys
from datetime import datetime


def format_log_line(message: str) -> str:
    # get current time in the format required by the project
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # remove extra spaces/newline from the input message
    stripped = message.strip()

    # if the message is empty, just use INFO as default action
    if not stripped:
        action = "INFO"
        rest = ""
    else:
        # first word = action, rest of line = message
        parts = stripped.split(maxsplit=1)
        action = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

    # build the final log line
    if rest:
        return f"{timestamp} [{action}] {rest}"
    return f"{timestamp} [{action}]"


def main() -> None:
    # program should get exactly one argument: log file name
    if len(sys.argv) != 2:
        print("Usage: python logger.py <logfile>", file=sys.stderr)
        sys.exit(1)

    log_filename = sys.argv[1]

    try:
        # open file in append mode so old logs are not erased
        with open(log_filename, "a", encoding="utf-8") as log_file:
            # keep reading messages from standard input
            for line in sys.stdin:
                msg = line.rstrip("\n")

                # QUIT stops the logger
                if msg == "QUIT":
                    break

                # format and write each log line
                formatted = format_log_line(msg)
                log_file.write(formatted + "\n")
                log_file.flush()

    except OSError as e:
        print(f"Logger file error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()