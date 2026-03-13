#!/usr/bin/env python3

import subprocess
import sys


def letters_only(s: str) -> bool:
    # check if string contains only letters
    return s.isalpha()


def normalize_text(s: str) -> str:
    # make input case-insensitive by converting to uppercase
    return s.strip().upper()


def log_message(logger_proc: subprocess.Popen, message: str) -> None:
    # send one log line to the logger process
    if logger_proc.stdin is not None:
        logger_proc.stdin.write(message + "\n")
        logger_proc.stdin.flush()


def send_encryption_command(enc_proc: subprocess.Popen, command: str) -> str:
    # send command to encryption process and read one response back
    if enc_proc.stdin is None or enc_proc.stdout is None:
        return "ERROR Encryption process pipes not available"

    enc_proc.stdin.write(command + "\n")
    enc_proc.stdin.flush()

    response = enc_proc.stdout.readline()
    if not response:
        return "ERROR No response from encryption process"

    return response.rstrip("\n")


def choose_from_history(history: list[str], label: str) -> str | None:
    # if no history exists, user has to enter a new string
    if not history:
        print("History is empty.")
        return None

    while True:
        print(f"\nSelect {label} from history:")
        for i, item in enumerate(history, start=1):
            print(f"{i}. {item}")
        print("0. Enter a new string instead")

        choice = input("Choice: ").strip()

        if not choice.isdigit():
            print("Error: Please enter a number.")
            continue

        idx = int(choice)

        if idx == 0:
            return None

        if 1 <= idx <= len(history):
            return history[idx - 1]

        print("Error: Invalid history selection.")


def get_string_with_history(history: list[str], purpose: str, store_new: bool) -> str | None:
    # ask user if they want to use history or type a new string
    while True:
        use_history = input(f"Use history for {purpose}? (y/n): ").strip().lower()

        if use_history in ("y", "yes"):
            chosen = choose_from_history(history, purpose)
            if chosen is not None:
                return chosen

        elif use_history in ("n", "no"):
            text = input(f"Enter string for {purpose}: ").strip()
            text = normalize_text(text)

            if not text:
                print("Error: Input cannot be empty.")
                continue

            if not letters_only(text):
                print("Error: Only letters are allowed.")
                continue

            # save new strings in history only when needed
            if store_new:
                history.append(text)

            return text

        else:
            print("Error: Please enter y or n.")


def handle_password(enc_proc: subprocess.Popen, logger_proc: subprocess.Popen, history: list[str]) -> None:
    # get password from user, but do not store it in history
    password = get_string_with_history(history, "password", store_new=False)
    if password is None:
        return

    log_message(logger_proc, "COMMAND password")

    # driver uses password, but backend uses PASSKEY
    response = send_encryption_command(enc_proc, f"PASSKEY {password}")

    if response.startswith("RESULT"):
        print("Password set successfully.")
        log_message(logger_proc, "RESULT password set successfully")
    else:
        print(response)
        log_message(logger_proc, f"ERROR password failed: {response}")


def handle_encrypt(enc_proc: subprocess.Popen, logger_proc: subprocess.Popen, history: list[str]) -> None:
    # get plaintext from history or user input
    text = get_string_with_history(history, "encrypt", store_new=True)
    if text is None:
        return

    log_message(logger_proc, "COMMAND encrypt")
    response = send_encryption_command(enc_proc, f"ENCRYPT {text}")

    if response.startswith("RESULT"):
        parts = response.split(maxsplit=1)
        result = parts[1] if len(parts) > 1 else ""
        print(f"Encrypted result: {result}")

        # save encrypted output in history too
        if result:
            history.append(result)

        log_message(logger_proc, "RESULT encrypt succeeded")
    else:
        print(response)
        log_message(logger_proc, f"ERROR encrypt failed: {response}")


def handle_decrypt(enc_proc: subprocess.Popen, logger_proc: subprocess.Popen, history: list[str]) -> None:
    # get ciphertext from history or user input
    text = get_string_with_history(history, "decrypt", store_new=True)
    if text is None:
        return

    log_message(logger_proc, "COMMAND decrypt")
    response = send_encryption_command(enc_proc, f"DECRYPT {text}")

    if response.startswith("RESULT"):
        parts = response.split(maxsplit=1)
        result = parts[1] if len(parts) > 1 else ""
        print(f"Decrypted result: {result} \n")

        # save decrypted output in history
        if result:
            history.append(result)

        log_message(logger_proc, "RESULT decrypt succeeded")
    else:
        print(response)
        log_message(logger_proc, f"ERROR decrypt failed: {response}")


def show_history(history: list[str], logger_proc: subprocess.Popen) -> None:
    # display everything saved during this run
    log_message(logger_proc, "COMMAND history")

    if not history:
        print("History is empty.")
        log_message(logger_proc, "RESULT history empty")
        return

    print("\nHistory:")
    for i, item in enumerate(history, start=1):
        print(f"{i}. {item}")
    print("\n")
    log_message(logger_proc, "RESULT history displayed")


def print_menu() -> None:
    # print user commands
    print("COMMANDS:")
    print("  PASSWORD")
    print("  ENCRYPT")
    print("  DECRYPT")
    print("  HISTORY")
    print("  QUIT")


def shutdown_process(proc: subprocess.Popen, quit_command: str = "QUIT") -> None:
    # try to tell child process to exit cleanly
    try:
        if proc.stdin is not None:
            proc.stdin.write(quit_command + "\n")
            proc.stdin.flush()
    except Exception:
        pass

    # wait a little bit, then force terminate if needed
    try:
        proc.wait(timeout=2)
    except Exception:
        try:
            proc.terminate()
        except Exception:
            pass


def main() -> None:
    # driver needs one argument: log file name
    if len(sys.argv) != 2:
        print("Usage: python driver.py <logfile>")
        sys.exit(1)

    log_filename = sys.argv[1]

    # history lasts only for this run
    history: list[str] = []

    try:
        # start logger process
        logger_proc = subprocess.Popen(
            [sys.executable, "logger.py", log_filename],
            stdin=subprocess.PIPE,
            text=True
        )

        # start encryption process
        enc_proc = subprocess.Popen(
            [sys.executable, "encryption.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )

    except Exception as e:
        print(f"Error starting child processes: {e}")
        sys.exit(1)

    try:
        log_message(logger_proc, "START Driver started")

        while True:
            print_menu()
            command = input("Enter command: ").strip().lower()

            if command == "password":
                handle_password(enc_proc, logger_proc, history)

            elif command == "encrypt":
                handle_encrypt(enc_proc, logger_proc, history)

            elif command == "decrypt":
                handle_decrypt(enc_proc, logger_proc, history)

            elif command == "history":
                show_history(history, logger_proc)

            elif command == "quit":
                log_message(logger_proc, "EXIT Driver exiting")
                shutdown_process(enc_proc, "QUIT")
                shutdown_process(logger_proc, "QUIT")
                break

            else:
                print("Error: Unknown command.")
                log_message(logger_proc, f"ERROR unknown command: {command}")

    except KeyboardInterrupt:
        print("\nInterrupted.")
        try:
            log_message(logger_proc, "EXIT Driver interrupted")
        except Exception:
            pass

        shutdown_process(enc_proc, "QUIT")
        shutdown_process(logger_proc, "QUIT")


if __name__ == "__main__":
    main()