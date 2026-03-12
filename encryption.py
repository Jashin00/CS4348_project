#!/usr/bin/env python3

import sys


def letters_only(s: str) -> bool:
    # return True only if the string has letters only
    return s.isalpha()


def normalize_text(s: str) -> str:
    # remove extra spaces and make input uppercase
    return s.strip().upper()


def vigenere_encrypt(plaintext: str, key: str) -> str:
    # store encrypted characters here
    result = []
    key_len = len(key)

    # go through each letter in the plaintext
    for i, ch in enumerate(plaintext):
        # convert letters to numbers 0 to 25
        p = ord(ch) - ord('A')
        k = ord(key[i % key_len]) - ord('A')

        # apply Vigenere encryption formula
        c = (p + k) % 26

        # convert back to a letter
        result.append(chr(c + ord('A')))

    return "".join(result)


def vigenere_decrypt(ciphertext: str, key: str) -> str:
    # store decrypted characters here
    result = []
    key_len = len(key)

    # go through each letter in the ciphertext
    for i, ch in enumerate(ciphertext):
        # convert letters to numbers 0 to 25
        c = ord(ch) - ord('A')
        k = ord(key[i % key_len]) - ord('A')

        # apply Vigenere decryption formula
        p = (c - k) % 26

        # convert back to a letter
        result.append(chr(p + ord('A')))

    return "".join(result)


def send_result(message: str = "") -> None:
    # send a success response back to the driver
    if message:
        print(f"RESULT {message}", flush=True)
    else:
        print("RESULT", flush=True)


def send_error(message: str) -> None:
    # send an error response back to the driver
    print(f"ERROR {message}", flush=True)


def main() -> None:
    # current_key keeps the passkey until user changes it
    current_key = None

    # keep reading commands from standard input
    for raw_line in sys.stdin:
        line = raw_line.rstrip("\n").strip()

        # reject empty command lines
        if not line:
            send_error("Empty command")
            continue

        # split into command and the rest of the line
        parts = line.split(maxsplit=1)
        command = parts[0].upper()
        argument = parts[1].strip() if len(parts) > 1 else ""

        if command == "QUIT":
            break

        # accept both PASS and PASSKEY because the project sheet is inconsistent
        elif command in ("PASSKEY"):
            if not argument:
                send_error("Password missing")
                continue

            key = normalize_text(argument)

            if not letters_only(key):
                send_error("Password must contain only letters")
                continue

            # save the current passkey
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