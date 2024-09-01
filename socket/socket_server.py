import socket
import sys
from os import path

DATA_SIZE = 1024
# hashes from script/string_encode
USER_MSGS = ["6151f939c902", "51ce6dc938e0", "9c2fc4e8a85d"]
SERVER_MSGS = [
    "Who's there?",
    "Eileen who?",
    "Eileen towards ColaCo, but any soda will do!",
]

HELP = [
    "Whisper the secret word, the answer lies within.",
    "What's the use of a door if you don't knock?",
    "You know the name",
]
FINISH = "EXIT"


def encode_s(string: str, length: int) -> str:
    """
    Shake 256 variable length encoding
    """
    try:
        from hashlib import shake_128
    except ImportError:
        print("You need to install hashlib to run this program")
        sys.exit(1)
    return shake_128(string.encode()).hexdigest(length)


def matches(encoded: str, user_input: str, length: int) -> bool:
    """
    Check if the user input matches hash
    """
    return encoded == encode_s(user_input.lower().strip(), length)


def send_ascii_art(c_socket, file_path="cola.whatever"):
    """
    Send client some ascii art (in bytes) - cola can with doorknob (as a welcome message/hint)
    along with length in bytes
    """
    try:
        from zstandard import ZstdDecompressor
    except ImportError:
        print("You need to install zstandard to run this program")
        sys.exit(1)

    package = bytearray()
    decompressor = ZstdDecompressor()  # decompress it

    with open(resource_path(file_path), "rb") as f:
        cola_art = f.read()
        decompressed_art = decompressor.decompress(cola_art)
        package += decompressed_art

    # print(f"Original size: {len(package)} bytes")
    if len(package) <= DATA_SIZE and len(package) >= 1:
        # If its more than 1024, the client will not be able to receive it in
        # one go
        # newline to ensure ascii art looks good
        c_socket.send("\n".encode() + package)
        return True, len(package)  # 464
    else:
        c_socket.send("No art for you ;(".encode())
        return False, 0


def ask_for_help():
    """Allow help flag (args)"""
    help_flag = {"-h", "--help"}
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in help_flag:
            # print("Usage: python3 socket_server.py")
            # go through items in array and print
            from random import choice

            print(choice(HELP))
            sys.exit(0)  # exit normally
        else:
            print(
                "Unrecognized option '%s', try me again with the right flag"
                % sys.argv[1]
            )
            sys.exit(1)  # exit with error
    else:
        print("Unfurl your banner. The quest begins. Scream for help if you need it.")


def resource_path(file_name):
    """
    Nuitka resource path for onefile mode
    basically to include a txt file inside exe
    https://nuitka.net/user-documentation/common-issue-solutions.html#onefile-finding-files
    """
    try:
        base_path = path.dirname(__file__)
    except Exception:
        base_path = path.abspath(".")
    return path.join(base_path, file_name)


def vigenere_decrypt(text: str, key: str):
    # https://gist.github.com/dssstr/aedbb5e9f2185f366c6d6b50fad3e4a4?permalink_comment_id=4035102#gistcomment-4035102

    result = ""
    alphabet = "0-123456789}ABCDEFGHIJKLMNOPQRST{UVWXYZ_abcdefghijklmnopqrstuvwxyz"
    for i in range(len(text)):
        letter_n = alphabet.index(text[i])
        key_n = alphabet.index(key[i % len(key)])
        value = (letter_n - key_n) % len(alphabet)
        result += alphabet[value]
    return result


def nth_digit(num, n):
    """
    Given a number, return the nth digit
    """
    return 0 if n < 0 else num // 10 ** (n - 1) % 10


def main():
    """
    All the server logic
    """
    ask_for_help()  # if client uses help flag
    s_socket = None
    c_socket = None  # default values
    try:
        s_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)  # server socket
        # put on random port, so client needs to port-scan each time
        # bind to any available port on localhost
        s_socket.bind(("127.0.0.1", 0))
        s_socket.listen(1)  # only allow 1 connection

        # #for debugging and lazy people
        # print(f"IP Address: {socket.gethostbyname(socket.gethostname())}")
        # port = s_socket.getsockname()[1]
        # print(f"Server listening on port: {port}")    # print socket if
        # debug=

        c_socket, _ = s_socket.accept()  # client socket
        proceed = True
        tracker = 0

        # send cola ascii art
        worked, leng = send_ascii_art(c_socket)  # 464
        if not worked:
            sys.exit(1)

        magic_num = tracker + 2  # random stuff to obfuscate
        # given a number, return the 2nd digit (this will be the length of the
        # shake digest) = 6
        shake_len = nth_digit(leng, magic_num)

        while proceed:
            data = c_socket.recv(DATA_SIZE).decode()
            if not data:
                print("You slammed the door on me!")
                proceed = False
            elif data == FINISH:
                proceed = False
            else:
                if data.lower().strip() == "help":
                    c_socket.send("--".encode())  # clue to use the flag
                    print("help")
                    proceed = False  # exit program
                    continue

                if tracker == 1:  # set up for punchline
                    print("Say this: I don't know")

                if tracker >= len(USER_MSGS):
                    c_socket.send(
                        "Congrats on making it this far, please check the other window".encode())
                    # trying to do this to make it more annoying to RE, and to
                    # push user to use socket library
                    flaggy = vigenere_decrypt(
                        "cV2JO8YDBCxhjhpkb6Tpl", USER_MSGS[magic_num]
                    )
                    print(
                        f"You have finally been unsubscribed from your ColaCo Plus Executive Membership. Goodbye! ColaCo{flaggy}"
                    )
                    proceed = False
                elif tracker < len(USER_MSGS) and matches(
                    encoded=USER_MSGS[tracker], user_input=data, length=shake_len
                ):
                    # send corresponding msg
                    c_socket.send(SERVER_MSGS[tracker].encode())
                    tracker += 1
                else:
                    print("I only respond to the right knock.")
                    c_socket.send(FINISH.encode())
                    proceed = False
    except Exception:
        print("Door is out of service, try again later.")
    except KeyboardInterrupt:
        print("You closed the door on me!")
    finally:
        if c_socket is not None:
            c_socket.send(FINISH.encode())
            c_socket.close()
        if s_socket is not None:
            s_socket.close()


if __name__ == "__main__":
    main()
