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

- Response code grammar
    
- It's safe to assume mail messages don't contain any command words or the SMTP message end indicator
"""


def parse_code(s: str) -> int:
    # TODO: implement code parsing
    """
    <response-code> ::= <resp-number> <whitespace> <arbitrary-text> <CRLF>
    <resp-number> ::= “250” | “354” | “500” | “501 | “503”
    <arbitrary-text> ::= any sequence of printable characters
    """
    pass


def wait_for_message() -> int:
    for line in sys.stdin:
        return parse_code(line)


class SMTPClientProcessor:
    def __init__(self, path):
        self.state = 0
        self.path = path
        self.message_flag = False
        self.message_buffer = ""

    def main(self):
        if self.path == "" or not os.path.exists(self.path):
            return
        with open(self.path, "r+") as fp:
            for line in fp.readlines():
                match state:
                    case 0:
                        # expecting From:
                        if line.startswith("From: "):
                            print(f"MAIL FROM: {line[6:].strip()}")
                            res = wait_for_message()
                            if res != 250:
                                print("QUIT")
                                break
                            self.state = 1
                        else:
                            print("QUIT")
                            self.state = 3
                    case 1:
                        # expecting To:
                        if line.startswith("To: "):
                            print(f"RCPT TO: {line[4:].strip()}")
                            # no need to change state
                        else:
                            # assume it's a message
                            self.read_message(line)
                    case 2:
                        # expecting data message
                        self.read_message(line)
                    case _:
                        sys.stderr.write("ERROR: INVALID STATE")
                        break

    def read_message(self, line: str):
        self.state = 2
        self.message_flag = True
        self.message_buffer += line


def main():
    # assume path is the first command line argument
    global state
    path = ""
    if len(sys.argv) > 1:
        path = sys.argv[1]
    processor = SMTPClientProcessor(path)


if __name__ == '__main__':
    main()
