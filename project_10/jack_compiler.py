import xml.etree.cElementTree as ET
import xml.etree.ElementTree as ElementTree

import re
from collections import deque

from jack_tokenizer import TokenType
from jack_tokenizer import Keyword


class Compiler:

    def __init__(self, tokenizer, output_file):
        self.tokenizer = tokenizer
        self.output_file = output_file
        self.root = None
        self.token = ""
        self._token_type = None

    def process(self, token, skip_advance=False):

        if self.token == token:
            if not skip_advance:
                self.advance()
        else:
            raise Exception(f"token {token} not found")

    def writeFile(self, tree):

        ElementTree.indent(tree)

        empty_tag_broken_string = re.sub(
            r"<(\w+)([^>]*)></\1>",
            r"<\1\2>\n</\1>",
            ElementTree.tostring(
                tree, encoding="unicode", short_empty_elements=False
            ),
        )
        formatted_xml = re.sub(
            r"(<\w+[^>]*>)(.*?)(</\w+>)", r"\1 \2 \3", empty_tag_broken_string
        )
        open(self.output_file +'.xml', "w").write(formatted_xml)

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
        self.root = ET.Element("class")
        self.advance()

        self.process("class")
        ET.SubElement(self.root, "keyword").text = "class"

        if self._token_type == TokenType.IDENTIFIER:
            ET.SubElement(self.root, "identifier").text = self.token
            self.advance()
        else:
            raise Exception("class name not found")

        self.process("{")
        ET.SubElement(self.root, "symbol").text = "{"

        while (
            self.token in {"static", "field"} and self._token_type == TokenType.KEYWORD
        ):
            self.compileClassVarDec(self.root)
            self.advance()

        while self.token in {"constructor", "function", "method"}:
            self.compileSubroutine(self.root)

        self.process("}", skip_advance=True)
        ET.SubElement(self.root, "symbol").text = "}"
        
        self.writeFile(self.root)

    def debug_tree(self, tree):

        empty_tag_broken_string = re.sub(
            r"<(\w+)([^>]*)></\1>",
            r"<\1\2>\n</\1>",
            ElementTree.tostring(tree, encoding="unicode", short_empty_elements=False),
        )
        formatted_xml = re.sub(
            r"(<\w+[^>]*>)(.*?)(</\w+>)", r"\1 \2 \3", empty_tag_broken_string
        )

        print(formatted_xml)

    def compileClassVarDec(self, tree):
        class_var_tree = ET.Element("classVarDec")

        if self.token in {"field", "static"} and self._token_type == TokenType.KEYWORD:
            ET.SubElement(class_var_tree, "keyword").text = self.token
        else:
            raise Exception(f"expecting field or static but found {self.token}")

        while not (self.token == ";" and self._token_type == TokenType.SYMBOL):
            self.advance()

            if self._token_type == TokenType.KEYWORD:
                ET.SubElement(class_var_tree, "keyword").text = self.token

            if self._token_type == TokenType.IDENTIFIER:
                ET.SubElement(class_var_tree, "identifier").text = self.token

            if self._token_type == TokenType.SYMBOL:
                ET.SubElement(class_var_tree, "symbol").text = self.token

        tree.append(class_var_tree)

    def compileSubroutine(self, tree):
        subroutine_tree = ET.Element("subroutineDec")

        if self.token in {"constructor", "function", "method"}:
            ET.SubElement(subroutine_tree, "keyword").text = self.token
        else:
            raise Exception(
                f"expecting constructor/function/method but found {self.token}"
            )

        self.advance()

        if self._token_type == TokenType.IDENTIFIER:
            ET.SubElement(subroutine_tree, "identifier").text = self.token
        elif self._token_type == TokenType.KEYWORD:
            ET.SubElement(subroutine_tree, "keyword").text = self.token

        self.advance()

        if self._token_type == TokenType.IDENTIFIER:
            ET.SubElement(subroutine_tree, "identifier").text = self.token

        self.advance()

        self.process("(")
        ET.SubElement(subroutine_tree, "symbol").text = "("

        self.compileParameterList(subroutine_tree)

        self.process(")")
        ET.SubElement(subroutine_tree, "symbol").text = ")"

        self.compileSubroutineBody(subroutine_tree)

        tree.append(subroutine_tree)

    def compileParameterList(self, tree):
        param_tree = ET.Element("parameterList")

        if self._token_type == TokenType.SYMBOL and self.token == ")":
            param_tree.text = ""
            tree.append(param_tree)
            return

        while not (self.token == ")" and self._token_type == TokenType.SYMBOL):
            if self._token_type == TokenType.KEYWORD:
                ET.SubElement(param_tree, "keyword").text = self.token

            elif self._token_type == TokenType.IDENTIFIER:
                ET.SubElement(param_tree, "identifier").text = self.token

            elif self._token_type == TokenType.SYMBOL:
                ET.SubElement(param_tree, "symbol").text = self.token

            self.advance()

        tree.append(param_tree)

    def compileSubroutineBody(self, tree):
        body_tree = ET.Element("subroutineBody")

        self.process("{")
        ET.SubElement(body_tree, "symbol").text = "{"

        if self.token == "}" and self._token_type == TokenType.SYMBOL:
            ET.SubElement(body_tree, "symbol").text = "}"
            tree.append(body_tree)
            return

        while self.token == "var" and self._token_type == TokenType.KEYWORD:
            self.compileVarDec(body_tree)
            self.advance()

        self.compileStatements(body_tree)

        self.process("}")
        ET.SubElement(body_tree, "symbol").text = "}"

        tree.append(body_tree)

    def compileVarDec(self, tree):
        varTree = ET.Element("varDec")

        if self.token == "var" and self._token_type == TokenType.KEYWORD:
            ET.SubElement(varTree, "keyword").text = "var"
        else:
            return

        while not (self.token == ";" and self._token_type == TokenType.SYMBOL):
            self.advance()

            if self._token_type == TokenType.KEYWORD:
                ET.SubElement(varTree, "keyword").text = self.token

            if self._token_type == TokenType.IDENTIFIER:
                ET.SubElement(varTree, "identifier").text = self.token

            if self._token_type == TokenType.SYMBOL:
                ET.SubElement(varTree, "symbol").text = self.token

        tree.append(varTree)

    def compileStatements(self, tree):

        statments_tree = ET.Element("statements")

        statement_types = {
            "if": self.compileIf,
            "while": self.compileWhile,
            "let": self.compileLet,
            "do": self.compileDo,
            "return": self.compileReturn,
        }

        while self.token in statement_types and self._token_type == TokenType.KEYWORD:
            statement_types[self.token](statments_tree)

        tree.append(statments_tree)

    def compileLet(self, tree):
        let_statement_tree = ET.Element("letStatement")

        self.process("let")
        ET.SubElement(let_statement_tree, "keyword").text = "let"

        if self._token_type == TokenType.IDENTIFIER:
            ET.SubElement(let_statement_tree, "identifier").text = self.token
        else:
            raise Exception(f"keyword expected but found {self.token}")

        self.advance()

        if self.token == "[" and self._token_type == TokenType.SYMBOL:
            self.process("[")
            ET.SubElement(let_statement_tree, "symbol").text = "["
            expression_list = self.extractExpression("[")
            self.compileExpression(let_statement_tree, expression_list)
            self.process("]")
            ET.SubElement(let_statement_tree, "symbol").text = "]"

        self.process("=")
        ET.SubElement(let_statement_tree, "symbol").text = "="

        expression_list = self.extractExpression(";")

        self.compileExpression(let_statement_tree, expression_list)

        self.process(";")
        ET.SubElement(let_statement_tree, "symbol").text = ";"

        tree.append(let_statement_tree)

    def extractExpression(self, start_symbol, debug=False, result=None, count=1):

        end_symbols = {"(": ")", "{": "}", "[": "]", ";": ";"}

        if result is None:
            result = deque()

        result.append([self.token, self._token_type])

        if debug:
            # self.debug_list(_list)
            pass

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

        if debug:
            print("list -> ", end="")
            self.debug_list(_list)

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

    def compileIf(self, tree):
        if_statement_tree = ET.Element("ifStatement")

        self.process("if")
        ET.SubElement(if_statement_tree, "keyword").text = "if"

        self.process("(")
        ET.SubElement(if_statement_tree, "symbol").text = "("

        expression_list = self.extractExpression("(")

        self.compileExpression(if_statement_tree, expression_list)

        self.process(")")
        ET.SubElement(if_statement_tree, "symbol").text = ")"

        self.process("{")
        ET.SubElement(if_statement_tree, "symbol").text = "{"

        self.compileStatements(if_statement_tree)

        self.process("}")
        ET.SubElement(if_statement_tree, "symbol").text = "}"

        if self.token == "else" and self._token_type == TokenType.KEYWORD:
            self.process("else")
            ET.SubElement(if_statement_tree, "keyword").text = "else"

            self.process("{")
            ET.SubElement(if_statement_tree, "symbol").text = "{"

            self.compileStatements(if_statement_tree)

            self.process("}")
            ET.SubElement(if_statement_tree, "symbol").text = "}"

        tree.append(if_statement_tree)

    def compileWhile(self, tree):

        while_statement_tree = ET.Element("whileStatement")

        self.process("while")
        ET.SubElement(while_statement_tree, "keyword").text = "while"

        self.process("(")
        ET.SubElement(while_statement_tree, "symbol").text = "("

        expression_list = self.extractExpression("(")

        self.compileExpression(while_statement_tree, expression_list)

        self.process(")")
        ET.SubElement(while_statement_tree, "symbol").text = ")"

        self.process("{")
        ET.SubElement(while_statement_tree, "symbol").text = "{"

        self.compileStatements(while_statement_tree)

        self.process("}")
        ET.SubElement(while_statement_tree, "symbol").text = "}"

        tree.append(while_statement_tree)

    def compileDo(self, tree):

        do_statement_tree = ET.Element("doStatement")

        self.process("do")
        ET.SubElement(do_statement_tree, "keyword").text = "do"

        expression_list = self.extractExpression(";")
        self.compileSubroutineCall(do_statement_tree, expression_list)

        self.process(";")
        ET.SubElement(do_statement_tree, "symbol").text = ";"

        tree.append(do_statement_tree)

    def debug_list(self, _list):
        print(" ".join([str(x[0]) for x in _list]))

    def compileSubroutineCall(self, tree, _list, debug=False):

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
            ET.SubElement(tree, "identifier").text = token
            token, token_type = advance(_list)
        else:
            raise Exception("Invalid subroutine")

        if token == "(" and token_type == TokenType.SYMBOL:
            ET.SubElement(tree, "symbol").text = "("

            expression_list = self.extractExpressionFromList("(", _list)

            self.compileExpressionList(tree, expression_list)
            ET.SubElement(tree, "symbol").text = ")"

        elif token == "." and token_type == TokenType.SYMBOL:
            process(".")
            ET.SubElement(tree, "symbol").text = "."

            ET.SubElement(tree, "identifier").text = token
            token, token_type = advance(_list)

            if not token == "(":
                raise Exception("Invalid subroutine")

            ET.SubElement(tree, "symbol").text = "("
            expression_list = self.extractExpressionFromList("(", _list)
            self.compileExpressionList(tree, expression_list)
            ET.SubElement(tree, "symbol").text = ")"

    def compileReturn(self, tree):

        return_statement_tree = ET.Element("returnStatement")

        self.process("return")
        ET.SubElement(return_statement_tree, "keyword").text = "return"

        if self.token == ";" and self._token_type == TokenType.SYMBOL:
            self.process(";")
            ET.SubElement(return_statement_tree, "symbol").text = ";"

            tree.append(return_statement_tree)
            return

        expression_list = self.extractExpression(";")
        self.compileExpression(return_statement_tree, expression_list)

        self.process(";")
        ET.SubElement(return_statement_tree, "symbol").text = ";"

        tree.append(return_statement_tree)

    def compileExpression(self, tree, _list):
        expression_tree = ET.Element("expression")

        bin_operators = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
        term_list = deque()


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
                self.compileTerm(expression_tree, term_list)
                term_list.clear()
                ET.SubElement(expression_tree, "symbol").text = token
                continue

            term_list.append([token, token_type])

        if term_list:
            self.compileTerm(expression_tree, term_list)

        tree.append(expression_tree)

    def compileTerm(self, tree, _list):
        term_tree = ET.Element("term")

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
                ET.SubElement(term_tree, "integerConstant").text = str(token)
            elif token_type == TokenType.STRING_CONST:
                ET.SubElement(term_tree, "stringConstant").text = token
            elif token_type == TokenType.KEYWORD and token in keyword_constants:
                ET.SubElement(term_tree, "keyword").text = token
            elif token_type == TokenType.IDENTIFIER:
                ET.SubElement(term_tree, "identifier").text = token
        else:
            token, token_type = _list.popleft()

            if token_type == TokenType.SYMBOL and token in unary_ops:
                ET.SubElement(term_tree, "symbol").text = token
                self.compileTerm(term_tree, _list)

            elif token_type == TokenType.IDENTIFIER:
                next_token, next_token_type = _list.popleft()

                if next_token == "[":
                    ET.SubElement(term_tree, "identifier").text = token
                    ET.SubElement(term_tree, "symbol").text = next_token
                    subexpression = self.extractExpressionFromList(next_token, _list)
                    self.compileExpression(term_tree, subexpression)
                    ET.SubElement(term_tree, "symbol").text = "]"

                else:
                    _list.appendleft([next_token, next_token_type])
                    _list.appendleft([token, token_type])
                    self.compileSubroutineCall(term_tree, _list)

            elif token == "(":
                ET.SubElement(term_tree, "symbol").text = "("
                subexpression = self.extractExpressionFromList("(", _list)

                self.compileExpression(term_tree, subexpression)
                ET.SubElement(term_tree, "symbol").text = ")"

        tree.append(term_tree)

    def compileExpressionList(self, tree, _list):

        expression_list_tree = ET.Element("expressionList")

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

                self.compileExpression(expression_list_tree, expression_list)
                expression_list.clear()
                ET.SubElement(expression_list_tree, "symbol").text = ","
                continue

            expression_list.append([token, token_type])

        # compile the last expression
        if expression_list:
            self.compileExpression(expression_list_tree, expression_list)

        tree.append(expression_list_tree)
