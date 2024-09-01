"""
NOT VISIBLE TO USER, Crypto stuff to try to make it more annoying to RE the socket server
"""

from hashlib import shake_128

ABC = "0-123456789}ABCDEFGHIJKLMNOPQRST{UVWXYZ_abcdefghijklmnopqrstuvwxyz"


def encode_s(string: str, length: int):
    """
    https://stackoverflow.com/a/59308715/4276951 (source of idea)
    changed to Shake (from SHA256) as its variable length, and I want to make the output be short to not flood the python file
    """
    return shake_128(string.encode()).hexdigest(length)


def matches(encoded: str, user_input: str, length: int) -> bool:
    return encoded == encode_s(user_input, length)


def runner(string: str, length=6):
    print(f"Original string: {string}")
    encoded = encode_s(string, length)
    print(f"Encoded: {encoded}")
    assert matches(encoded, string, length)
    return encoded


def array_to_shake(arr: list) -> list:
    return [encode_s(x.lower(), 6) for x in arr]


def vigenere(text: str, key: str, encrypt=True):
    """
    Source: # https://gist.github.com/dssstr/aedbb5e9f2185f366c6d6b50fad3e4a4?permalink_comment_id=4035102#gistcomment-4035102
    Hiding end flag via vigenere cipher but my code will decipher it, just to throw another wrench in the mix
    """
    result = ""

    for i, char in enumerate(text):
        letter_n = ABC.index(char)
        key_n = ABC.index(key[i % len(key)])

        if encrypt:
            value = (letter_n + key_n) % len(ABC)
        else:
            value = (letter_n - key_n) % len(ABC)

        result += ABC[value]

    return result


def vigenere_encrypt(text, key):
    return vigenere(text=text, key=key, encrypt=True)


def vigenere_decrypt(text, key):
    return vigenere(text=text, key=key, encrypt=False)


def main():

    USER_MSGS = ["Knock Knock", "Eileen", "I Don't Know"]
    converted = array_to_shake(USER_MSGS)
    print("Array:", converted)

    runner_flag = "{s0ck3t5_4r3_4m4z1ng}"
    key = converted[2]
    runner(runner_flag, 6)

    vig = vigenere_encrypt(runner_flag, key)
    print("vig_en:", vig)
    print("vig_dec:", vigenere_decrypt(vig, key))


if __name__ == "__main__":
    main()
