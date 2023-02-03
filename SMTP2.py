"""
I certify that no unauthorized assistance has been received or given in the completion of this work
Signed: Oliver Chen
Date: TODO
"""

import sys
import os

"""
TODO: Checklist
- [ ] read a forward file
- [ ] recognize a "From:" line
- [ ] send a SMTP "MAIL FROM:" server message
- [ ] recognize a To: line
- [ ] send a SMTP "RCPT TO:" server message
- [ ] recognize an arbitary message until EOF or the next command
- [ ] send a SMTP "DATA" server message and ending

Other Notes
- It's safe to assume mail messages don't contain any command words or the SMTP message end indicator
"""


class ResponseParser:
    def __init__(self, message: str):
        self.stream = iter(message)
        self.next = next(self.stream)
        self.code = -1

    def put_next(self):
        try:
            self.next = next(self.stream)
        except StopIteration:
            self.next = ""

    def consume(self, s: str):
        for c in s:
            if self.next != c:
                return False
            self.put_next()
        return True

    def parse_code(self) -> int:
        code = self.resp_number()
        if self.whitespace() and self.arbitrary() and self.crlf():
            return code
        return -1

    def resp_number(self):
        for num in ["250", "354"]:
            if self.consume(num):
                return int(num)

    def whitespace(self):
        if self.next not in (" ", "\t"):
            return False

        self.put_next()
        self.whitespace()
        return True

    def arbitrary(self):
        if self.next == "\n":
            return False

        while self.next != "\n":
            self.put_next()

        return True

    def crlf(self):
        return self.next == "\n"


def parse_code(s: str) -> int:
    """
    <response-code> ::= <resp-number> <whitespace> <arbitrary-text> <CRLF>
    <resp-number> ::= “250” | “354” | “500” | “501 | “503”
    <arbitrary-text> ::= any sequence of printable characters
    """
    # int code if recognized, -1 if not
    # we assume always int code
    return ResponseParser(s).parse_code()


def wait_for_response() -> (int, str):
    for line in sys.stdin:
        return parse_code(line), line
    return -1, None


class SMTPClientProcessor:
    def __init__(self, path):
        self.state = 0
        self.path = path
        self.message_flag = False
        self.message_buffer = ""

    def main(self):
        lines = self.get_lines()
        if lines is None:
            return

        for line in lines:
            match self.state:
                case 0:
                    # expecting From:
                    if line.startswith("From: "):
                        print(f"MAIL FROM: {line[6:].strip()}")
                        self.react_to_response(250, 1)
                    else:
                        print("QUIT")
                        self.state = -1
                case 1:
                    # expecting To:
                    if line.startswith("To: "):
                        print(f"RCPT TO: {line[4:].strip()}")
                        self.react_to_response(250, 2)
                    else:
                        print("QUIT")
                        self.state = -1
                case 2:
                    # expecting To: or data message
                    if line.startswith("To: "):
                        print(f"RCPT TO: {line[4:].strip()}")
                    else:
                        print("DATA")
                        self.react_to_response(354, 3)
                        self.read_message(line)
                case 3:
                    # expecting data message
                    self.read_message(line)
                case _:
                    # sys.stderr.write("ERROR: INVALID STATE")
                    break
        if self.state != -1:
            print(self.message_buffer)
            self.react_to_response(250)
            print("\n.\n")
            print("QUIT")

    def get_lines(self):
        if self.path == "" or not os.path.exists(self.path):
            return None
        with open(self.path, "r+") as fp:
            return fp.readlines()

    def read_message(self, line: str):
        self.state = 3
        self.message_flag = True
        self.message_buffer += line

    def react_to_response(self, expected_code: int, next_state: int = -1):
        res = wait_for_response()
        code = res[0]
        message = res[1]
        sys.stderr.write(message)
        if code != expected_code:
            print("QUIT")
            self.state = -1
        else:
            self.state = next_state


def main():
    # assume path is the first command line argument
    path = ""
    if len(sys.argv) > 1:
        path = sys.argv[1]
    processor = SMTPClientProcessor(path)
    processor.main()


if __name__ == '__main__':
    main()
