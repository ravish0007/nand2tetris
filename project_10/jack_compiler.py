import xml.etree.cElementTree as ET
import xml.etree.ElementTree as ElementTree

from jack_tokenizer import TokenType
from jack_tokenizer import Keyword


class Compiler:

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.root = None
        self.token = ""
        self._token_type = None

    def process(self, token):

        if self.token == token:
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
            self.advance()

        tree = ET.ElementTree(self.root)
        ElementTree.indent(self.root)
        open("filename.xml", "w").write(
            ElementTree.tostring(
                self.root, encoding="unicode", short_empty_elements=False
            )
        )
        # tree.write("filename.xml")

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

        # TODO: handle array

        self.process("=")
        ET.SubElement(let_statement_tree, "symbol").text = "="

        expression_list = self.extractExpression(";")
        self.compileExpression(let_statement_tree, expression_list)

        self.process(";")
        ET.SubElement(let_statement_tree, "symbol").text = ";"

        tree.append(let_statement_tree)

    def extractExpression(self, start_symbol):

        end_symbols = {"(": ")", "{": "}", ";": ";"}

        store = []
        temp_q = [(start_symbol, TokenType.SYMBOL)]

        while temp_q:
            if (
                self.token in end_symbols.values()
                and self.token == end_symbols[start_symbol]
                and self._token_type == TokenType.SYMBOL
            ):
                while temp_q and temp_q[-1][0] != start_symbol:
                    store.append(temp_q.pop())

                bracket = temp_q.pop()

                if len(temp_q) > 0:
                    store.append(bracket)
                else:
                    break
            temp_q.append((self.token, self._token_type))
            self.advance()

        store.reverse()
        return store

    def compileIf(self, tree):
        if_statement_tree = ET.Element("ifStatement")

        self.process("if")
        ET.SubElement(if_statement_tree, "keyword").text = "if"

        self.process("(")
        ET.SubElement(if_statement_tree, "symbol").text = "("

        expression_list = self.extractExpression("(")

        # if expression_list:
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

        # expression_list = self.extractExpression(";")
        self.compileSubroutineCall(do_statement_tree)

        self.process(";")
        ET.SubElement(do_statement_tree, "symbol").text = ";"

        tree.append(do_statement_tree)

    def compileSubroutineCall(self, tree):

        ET.SubElement(tree, "identifier").text = self.token
        self.advance()

        if self.token == "(" and self._token_type == TokenType.SYMBOL:

            self.process("(")
            ET.SubElement(tree, "symbol").text = "("
            expression_list = self.extractExpression("(")
            self.compileExpressionList(tree, expression_list)
            self.process(")")
            ET.SubElement(tree, "symbol").text = ")"

        elif self.token == "." and self._token_type == TokenType.SYMBOL:
            self.process(".")
            ET.SubElement(tree, "symbol").text = "."

            ET.SubElement(tree, "identifier").text = self.token
            self.advance()

            self.process("(")
            ET.SubElement(tree, "symbol").text = "("
            expression_list = self.extractExpression("(")
            self.compileExpressionList(tree, expression_list)
            self.process(")")
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

    def compileExpression(self, tree, expression_list):
        expression_tree = ET.Element("expression")
        expression_tree.text = ""

        # print(expression_list)

        expression_tree.text = " ".join(str(x[0]) for x in expression_list)

        # while not (self.token == ";" and self._token_type == TokenType.SYMBOL):
        #     expression_tree.text += f" {self.token}"
        #     self.advance()
        tree.append(expression_tree)

    def compileTerm(self, tree):
        pass

    def compileExpressionList(self, tree, _list):

        expression_list_tree = ET.Element("expressionList")
        expression_list_tree.text = ""

        # print(expression_list)

        expression_list_tree.text = " ".join(str(x[0]) for x in _list)

        # while not (self.token == ";" and self._token_type == TokenType.SYMBOL):
        #     expression_tree.text += f" {self.token}"
        #     self.advance()
        tree.append(expression_list_tree)

        pass
