from enum import Enum
from string import punctuation
import re


class TokenType(Enum):
    KEYWORD = 0
    SYMBOL = 1
    IDENTIFIER = 2
    INT_CONST = 3
    STRING_CONST = 4


class Keyword(Enum):
    CLASS = 0
    METHOD = 1
    FUNCTION = 2
    CONSTRUCTOR = 3
    INT = 4
    BOOLEAN = 5
    CHAR = 6
    VOID = 7
    VAR = 8
    STATIC = 9
    FIELD = 10
    LET = 11
    DO = 12
    IF = 13
    ELSE = 14
    WHILE = 15
    RETURN = 16
    TRUE = 17
    FALSE = 18
    NULL = 19
    THIS = 20


class Tokenizer:
    def __init__(self, input_file):
        self.file = open(input_file)
        self.current_line = ""
        self.token = None
        self._token_type = None

        self.keywords = {
            "class": Keyword.CLASS,
            "method": Keyword.METHOD,
            "function": Keyword.FUNCTION,
            "constructor": Keyword.CONSTRUCTOR,
            "int": Keyword.INT,
            "boolean": Keyword.BOOLEAN,
            "char": Keyword.CHAR,
            "void": Keyword.VOID,
            "var": Keyword.VAR,
            "static": Keyword.STATIC,
            "field": Keyword.FIELD,
            "let": Keyword.LET,
            "do": Keyword.DO,
            "if": Keyword.IF,
            "else": Keyword.ELSE,
            "while": Keyword.WHILE,
            "return": Keyword.RETURN,
            "true": Keyword.TRUE,
            "false": Keyword.FALSE,
            "null": Keyword.NULL,
            "this": Keyword.THIS,
        }

    def hasMoreTokens(self):
        previous_location = self.file.tell()
        status = self.file.readline() != ""
        self.file.seek(previous_location)
        return status or len(self.current_line) > 0

    def match_keyword(self, string):
        for keyword in self.keywords:
            if self.current_line.startswith(keyword):
                remaining = self.current_line[len(keyword) :].strip()
                return [keyword, remaining]

        return None

    def match_symbol(self, string):
        if string[0] in punctuation:
            return [string[0], string[1:].strip()]
        return None

    def match_number(self, string):
        match = re.match(r"^(\d+)", string)
        if match:
            start, end = match.span()
            return [int(string[start:end].strip()), string[end:].strip()]
        return None

    def match_string(self, string):
        match = re.match(r'^"(.+)"', string)
        if match:
            start, end = match.span()
            return [string[start + 1 : end - 1].strip(), string[end:].strip()]
        return None

    def match_identifier(self, string):
        match = re.match(r"^(\D\w*)", string)
        if match:
            start, end = match.span()
            return [string[start:end].strip(), string[end:].strip()]
        return None

    def process_match(self, result, token_type):
        token, remaining = result
        self._token_type = token_type
        self.token = token
        self.current_line = remaining

    def advance(self):
        comment_detected = False
        self.token = None
        self._token_type = None

        while True:
            if not self.hasMoreTokens():
                break

            if self.current_line:
                result = self.match_keyword(self.current_line)
                if result:
                    self.process_match(result, TokenType.KEYWORD)
                    break

                result = self.match_number(self.current_line)
                if result:
                    self.process_match(result, TokenType.INT_CONST)
                    break

                result = self.match_string(self.current_line)
                if result:
                    self.process_match(result, TokenType.STRING_CONST)
                    break

                result = self.match_symbol(self.current_line)
                if result:
                    self.process_match(result, TokenType.SYMBOL)
                    break

                result = self.match_identifier(self.current_line)
                if result:
                    self.process_match(result, TokenType.IDENTIFIER)
                    break

            self.current_line = self.file.readline().strip()

            if self.current_line.startswith("//"):
                self.current_line = ""

            elif "//" in self.current_line:
                self.current_line = self.current_line.split("//")[0].strip()

            elif self.current_line.startswith("/*") and self.current_line.endswith(
                "*/"
            ):
                self.current_line = ""

            elif self.current_line.startswith("/*"):
                self.current_line = ""
                comment_detected = True

            elif self.current_line.endswith("*/"):
                self.current_line = ""
                comment_detected = False

            if comment_detected:
                self.current_line = ""

    def token_type(self):
        return self._token_type

    def keyword(self):
        if self.token in self.keywords:
            return self.keywords[self.token]

        raise Exception(f"keyword {self.token} not found")

    def symbol(self):
        return self.token

    def identifier(self):
        return self.token

    def int_val(self):
        return self.token

    def string_val(self):
        return self.token
