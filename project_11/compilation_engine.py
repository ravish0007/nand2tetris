from collections import deque
from jack_tokenizer import TokenType


from symbol_table import (
    ClassSymbolTable,
    SubroutineTable,
    ClassSymbolType,
    SubroutineSymbolType,
)


label_count = 0


class CompilationEngine:

    def __init__(self, tokenizer, vm_writer):
        self.tokenizer = tokenizer
        self.vm_writer = vm_writer
        self.root = None
        self.token = ""
        self._token_type = None

        self.class_symbol_table = None
        self.subroutine_symbol_table = None

    @staticmethod
    def get_label():
        global label_count
        label = f"L{label_count}"
        label_count += 1
        return label

    def process(self, token, skip_advance=False):

        if self.token == token:
            if not skip_advance:
                self.advance()
        else:
            raise Exception(f"token {token} not found")

    def advance(self):

        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            self.token, self._token_type = (
                self.tokenizer.token,
                self.tokenizer.token_type(),
            )

        else:
            raise Exception("No more tokens")

    def compileClass(self):

        self.advance()
        self.process("class")

        if self._token_type == TokenType.IDENTIFIER:
            # declaration of class_symbol_table
            class_name = self.token
            self.class_symbol_table = ClassSymbolTable(class_name)
            self.advance()
        else:
            raise Exception("class name not found")

        self.process("{")

        while (
            self.token in {"static", "field"} and self._token_type == TokenType.KEYWORD
        ):
            self.compileClassVarDec()
            self.advance()

        while self.token in {"constructor", "function", "method"}:
            self.compileSubroutine()

        self.process("}", skip_advance=True)

    def compileClassVarDec(self):

        class_symbol_type = None

        if self.token in {"field", "static"} and self._token_type == TokenType.KEYWORD:
            if self.token == "field":
                class_symbol_type = ClassSymbolType.FIELD
            elif self.token == "static":
                class_symbol_type = ClassSymbolType.STATIC
        else:
            raise Exception(f"expecting field or static but found {self.token}")

        ### extracting type

        self.advance()

        if self._token_type in {TokenType.KEYWORD, TokenType.IDENTIFIER}:
            pass
        else:
            raise Exception(
                f"type not found in static|field declaration in class found {self._token_type}",
            )

        var_type = self.token

        while not (self.token == ";" and self._token_type == TokenType.SYMBOL):
            self.advance()

            if self._token_type == TokenType.IDENTIFIER:
                self.class_symbol_table.add_entry(
                    class_symbol_type, self.token, var_type
                )

    def compileSubroutine(self):
        if self.token in {"constructor", "function", "method"}:
            pass
        else:
            raise Exception(
                f"expecting constructor/function/method but found {self.token}"
            )

        subroutine_type = self.token
        self.advance()

        subroutine_return_type = self.token
        self.advance()

        subroutine_name = self.token

        ## creating subroutine table
        self.subroutine_symbol_table = SubroutineTable(
            subroutine_name,
            subroutine_type,
            subroutine_return_type,
            self.class_symbol_table,
        )

        self.advance()

        self.process("(")

        self.compileParameterList()

        self.process(")")

        self.compileSubroutineBody()

    def compileParameterList(self):

        if self._token_type == TokenType.SYMBOL and self.token == ")":
            return

        while not (self.token == ")" and self._token_type == TokenType.SYMBOL):

            arg_type = self.token
            self.advance()

            if self._token_type == TokenType.IDENTIFIER:
                pass
            else:
                raise Exception(f" {self.token} arg name not valid")

            arg_name = self.token

            self.subroutine_symbol_table.add_entry(
                SubroutineSymbolType.ARG, arg_name, arg_type
            )

            self.advance()

            if self._token_type == TokenType.SYMBOL and self.token == ",":
                self.advance()

    def compileSubroutineBody(self):

        self.process("{")

        if self.token == "}" and self._token_type == TokenType.SYMBOL:
            return

        while self.token == "var" and self._token_type == TokenType.KEYWORD:
            self.compileVarDec()
            self.advance()

        self.vm_writer.write_function(self.subroutine_symbol_table)
        if self.subroutine_symbol_table.subroutine_type == "constructor":
            field_count = self.subroutine_symbol_table.jack_class.field_symbols_count
            self.vm_writer.write_push("constant", field_count)
            self.vm_writer.write_call("Memory", "alloc", 1)
            self.vm_writer.write_pop("pointer", 0)
        elif self.subroutine_symbol_table.subroutine_type == "method":
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)

        self.compileStatements()

        self.process("}")

    def compileVarDec(self):

        if self.token == "var" and self._token_type == TokenType.KEYWORD:
            pass
        else:
            return

        self.advance()

        if self._token_type in {TokenType.KEYWORD, TokenType.IDENTIFIER}:
            pass
        else:
            raise Exception(
                f"type not found in var declaration in subroutine {self.subroutine_symbol_table.name} found {self._token_type}",
            )

        var_type = self.token

        while not (self.token == ";" and self._token_type == TokenType.SYMBOL):

            self.advance()

            if self._token_type == TokenType.IDENTIFIER:
                self.subroutine_symbol_table.add_entry(
                    SubroutineSymbolType.VAR, self.token, var_type
                )

    def compileStatements(self):

        statement_types = {
            "if": self.compileIf,
            "while": self.compileWhile,
            "let": self.compileLet,
            "do": self.compileDo,
            "return": self.compileReturn,
        }

        while self.token in statement_types and self._token_type == TokenType.KEYWORD:
            statement_types[self.token]()

    def compileLet(self):

        self.process("let")

        if self._token_type == TokenType.IDENTIFIER:
            pass
        else:
            raise Exception(f"keyword expected but found {self.token}")

        variable = self.token
        symbol = self.subroutine_symbol_table.get_symbol(variable)

        self.advance()

        # process array
        if self.token == "[" and self._token_type == TokenType.SYMBOL:
            self.process("[")
            expression_list = self.extractExpression("[")
            self.compileExpression(expression_list)
            self.process("]")

            self.process("=")

            self.vm_writer.write_push_symbol(symbol)
            self.vm_writer.write("add")

            expression_list = self.extractExpression(";")
            self.compileExpression(expression_list)

            self.vm_writer.write_pop("temp", 0)
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)
            self.process(";")

        else:
            self.process("=")

            expression_list = self.extractExpression(";")
            self.compileExpression(expression_list)

            self.vm_writer.write_pop_symbol(symbol)

            self.process(";")

    def extractExpression(self, start_symbol, debug=False, result=None, count=1):

        end_symbols = {"(": ")", "{": "}", "[": "]", ";": ";"}

        if result is None:
            result = deque()

        result.append([self.token, self._token_type])

        is_closing_token = (
            self.token in end_symbols.values()
            and self.token == end_symbols[start_symbol]
            and self._token_type == TokenType.SYMBOL
        )

        new_count = count
        if is_closing_token:
            new_count -= 1
        elif self.token == start_symbol:
            new_count += 1

        if new_count == 0:
            result.pop()

            return result

        self.advance()
        return self.extractExpression(start_symbol, debug, result, new_count)

    def extractExpressionFromList(
        self, start_symbol, _list, debug=False, result=None, count=1
    ):

        end_symbols = {"(": ")", "{": "}", "[": "]", ";": ";"}

        if result is None:
            result = deque()

        token, token_type = _list.popleft()
        result.append([token, token_type])

        is_closing_token = (
            token in end_symbols.values()
            and token == end_symbols[start_symbol]
            and token_type == TokenType.SYMBOL
        )

        new_count = count
        if is_closing_token:
            new_count -= 1
        elif token == start_symbol:
            new_count += 1

        if new_count == 0:
            result.pop()

            return result

        return self.extractExpressionFromList(
            start_symbol, _list, debug, result, new_count
        )

    def compileIf(self):

        self.process("if")

        self.process("(")

        expression_list = self.extractExpression("(")
        self.compileExpression(expression_list)

        self.process(")")
        self.process("{")

        false_label = CompilationEngine.get_label()
        end_label = CompilationEngine.get_label()
        self.vm_writer.write_if(false_label)

        self.compileStatements()

        self.vm_writer.write_goto(end_label)
        self.vm_writer.write_label(false_label)

        self.process("}")

        if self.token == "else" and self._token_type == TokenType.KEYWORD:
            self.process("else")
            self.process("{")

            self.compileStatements()

            self.process("}")

        self.vm_writer.write_label(end_label)

    def compileWhile(self):

        self.process("while")
        self.process("(")

        while_label = CompilationEngine.get_label()
        end_label = CompilationEngine.get_label()

        self.vm_writer.write_label(while_label)

        expression_list = self.extractExpression("(")
        self.compileExpression(expression_list)

        self.process(")")

        self.process("{")

        self.vm_writer.write_if(end_label)

        self.compileStatements()

        self.vm_writer.write_goto(while_label)
        self.vm_writer.write_label(end_label)

        self.process("}")

    def compileDo(self):

        self.process("do")

        expression_list = self.extractExpression(";")
        self.compileSubroutineCall(expression_list)

        self.vm_writer.write_pop("temp", 0)

        self.process(";")

    def compileSubroutineCall(self, _list):

        if not _list:
            raise Exception("Empty expression_list while parsing subroutine")

        def advance(_list):
            if _list:
                token, token_type = _list.popleft()
                return token, token_type

        def process(string):
            nonlocal token
            nonlocal token_type
            if string == token:
                token, token_type = advance(_list)
            else:
                raise Exception(f"processing  {token} but found {string}")

        token, token_type = advance(_list)

        if token_type == TokenType.IDENTIFIER:
            previous_token = function_name = token
            function_class = self.subroutine_symbol_table.jack_class.class_name
            token, token_type = advance(_list)
        else:
            raise Exception("Invalid subroutine")

        # default function calls
        if token == "(" and token_type == TokenType.SYMBOL:

            arg_count = 1
            self.vm_writer.write_push("pointer", 0)

            expression_list = self.extractExpressionFromList("(", _list)
            arg_count += self.compileExpressionList(expression_list)

            self.vm_writer.write_call(function_class, function_name, arg_count)

        elif token == "." and token_type == TokenType.SYMBOL:
            process(".")

            function_name = token
            obj = self.subroutine_symbol_table.get_symbol(previous_token)
            if obj:
                _, _type, _ = obj
                function_class = _type
                arg_count = 1
                self.vm_writer.write_push_symbol(obj)
            else:
                arg_count = 0
                function_class = previous_token

            token, token_type = advance(_list)
            if not token == "(":
                raise Exception("Invalid subroutine")

            expression_list = self.extractExpressionFromList("(", _list)
            arg_count += self.compileExpressionList(expression_list)
            self.vm_writer.write_call(function_class, function_name, arg_count)

    def compileReturn(self):
        self.process("return")

        if self.token == ";" and self._token_type == TokenType.SYMBOL:
            self.vm_writer.write_int(0)
            self.vm_writer.write_return()
            self.process(";")
            return

        expression_list = self.extractExpression(";")
        self.compileExpression(expression_list)
        self.vm_writer.write_return()
        self.process(";")

    def compileExpression(self, _list):
        # all the in between unary operator will be eclosed in brackets (op term)

        bin_operators = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
        term_list = deque()

        previous_operator = None

        while _list:
            token, token_type = _list.popleft()

            if token in ["(", "["] and token_type == TokenType.SYMBOL:

                term_list.append([token, token_type])
                subexpression = self.extractExpressionFromList(token, _list)
                term_list.extend(subexpression)
                term_list.append([")" if token == "(" else "]", token_type])
                continue

            is_unary = (
                token in ["-", "~"]
                and token_type == TokenType.SYMBOL
                and len(term_list) == 0
            )

            if (
                token in bin_operators
                and token_type == TokenType.SYMBOL
                and not is_unary
            ):  # evading just "-" unary, term
                self.compileTerm(term_list)

                if previous_operator:
                    self.vm_writer.write_arithmetic(previous_operator, False)

                previous_operator = token

                term_list.clear()
                continue

            term_list.append([token, token_type])

        if term_list:
            self.compileTerm(term_list)
            if previous_operator:
                self.vm_writer.write_arithmetic(previous_operator, False)

    def compileTerm(self, _list):

        keyword_constants = [
            "true",
            "false",
            "null",
            "this",
        ]

        unary_ops = ["-", "~"]

        if len(_list) == 1:
            token, token_type = _list.popleft()
            if token_type == TokenType.INT_CONST:
                self.vm_writer.write_int(token)
            elif token_type == TokenType.STRING_CONST:
                self.vm_writer.write_string(token)
            elif token_type == TokenType.KEYWORD and token in keyword_constants:
                if token == "this":
                    self.vm_writer.write_push("pointer", 0)
                elif token in ["null", "false"]:
                    self.vm_writer.write_int(0)
                elif token == "true":
                    self.vm_writer.write_int(0)
                    self.vm_writer.write("not")
            elif token_type == TokenType.IDENTIFIER:
                symbol = self.subroutine_symbol_table.get_symbol(token)
                self.vm_writer.write_push_symbol(symbol)
        else:
            token, token_type = _list.popleft()

            if token_type == TokenType.SYMBOL and token in unary_ops:
                self.compileTerm(_list)
                self.vm_writer.write_arithmetic(token, is_unary=True)

            elif token_type == TokenType.IDENTIFIER:
                next_token, next_token_type = _list.popleft()

                if next_token == "[":
                    subexpression = self.extractExpressionFromList(next_token, _list)
                    self.compileExpression(subexpression)

                    symbol = self.subroutine_symbol_table.get_symbol(token)
                    self.vm_writer.write_push_symbol(symbol)
                    self.vm_writer.write("add")

                    self.vm_writer.write_pop("pointer", 1)
                    self.vm_writer.write_push("that", 0)

                else:
                    _list.appendleft([next_token, next_token_type])
                    _list.appendleft([token, token_type])
                    self.compileSubroutineCall(_list)

            elif token == "(":
                subexpression = self.extractExpressionFromList("(", _list)
                self.compileExpression(subexpression)

    def compileExpressionList(self, _list):

        num_expressions = 0

        expression_list = deque()

        while _list:
            token, token_type = _list.popleft()

            if token in ["(", "["] and token_type == TokenType.SYMBOL:

                expression_list.append([token, token_type])
                subexpression = self.extractExpressionFromList(token, _list)
                expression_list.extend(subexpression)
                expression_list.append([")" if token == "(" else "]", token_type])

                continue

            if token == "," and token_type == TokenType.SYMBOL:
                num_expressions += 1

                self.compileExpression(expression_list)
                expression_list.clear()
                continue

            expression_list.append([token, token_type])

        # compile the last expression
        if expression_list:
            num_expressions += 1
            self.compileExpression(expression_list)

        return num_expressions
