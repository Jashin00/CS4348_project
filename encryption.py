#!/usr/bin/env python3

import sys


def letters_only(s: str) -> bool:
    return s.isalpha()


def normalize_text(s: str) -> str:
    return s.strip().upper()


def vigenere_encrypt(plaintext: str, key: str) -> str:
    result = []
    key_len = len(key)

    for i, ch in enumerate(plaintext):
        p = ord(ch) - ord('A')
        k = ord(key[i % key_len]) - ord('A')
        c = (p + k) % 26
        result.append(chr(c + ord('A')))

    return "".join(result)


def vigenere_decrypt(ciphertext: str, key: str) -> str:
    result = []
    key_len = len(key)

    for i, ch in enumerate(ciphertext):
        c = ord(ch) - ord('A')
        k = ord(key[i % key_len]) - ord('A')
        p = (c - k) % 26
        result.append(chr(p + ord('A')))

    return "".join(result)


def send_result(message: str = "") -> None:
    if message:
        print(f"RESULT {message}", flush=True)
    else:
        print("RESULT", flush=True)


def send_error(message: str) -> None:
    print(f"ERROR {message}", flush=True)


def main() -> None:
    current_key = None

    for raw_line in sys.stdin:
        line = raw_line.rstrip("\n").strip()

        if not line:
            send_error("Empty command")
            continue

        parts = line.split(maxsplit=1)
        command = parts[0].upper()
        argument = parts[1].strip() if len(parts) > 1 else ""

        if command == "QUIT":
            break

        elif command in ("PASS"):
            if not argument:
                send_error("Password missing")
                continue

            key = normalize_text(argument)

            if not letters_only(key):
                send_error("Password must contain only letters")
                continue

            current_key = key
            send_result()

        elif command == "ENCRYPT":
            if current_key is None:
                send_error("Password not set")
                continue

            if not argument:
                send_error("Missing text to encrypt")
                continue

            text = normalize_text(argument)

            if not letters_only(text):
                send_error("Input must contain only letters")
                continue

            encrypted = vigenere_encrypt(text, current_key)
            send_result(encrypted)

        elif command == "DECRYPT":
            if current_key is None:
                send_error("Password not set")
                continue

            if not argument:
                send_error("Missing text to decrypt")
                continue

            text = normalize_text(argument)

            if not letters_only(text):
                send_error("Input must contain only letters")
                continue

            decrypted = vigenere_decrypt(text, current_key)
            send_result(decrypted)

        else:
            send_error("Unknown command")


if __name__ == "__main__":
    main()