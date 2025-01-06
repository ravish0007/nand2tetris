#!/usr/bin/python
import sys

from jack_tokenizer import Tokenizer, TokenType

# from jack_compiler import Compiler

file = sys.argv[1]
outputfile_name = sys.argv[1].split("/")[-1][:-5] + ".xml"

outfile = open(outputfile_name, "w")
outfile.write("<tokens>\n")


tokenizer = Tokenizer(file)

while tokenizer.hasMoreTokens():
    tokenizer.advance()
    token_type = tokenizer.token_type()

    if not token_type:
        continue

    token = tokenizer.token

    if token_type == TokenType.KEYWORD:
        outfile.write(f"<keyword> {token} </keyword>\n")

    if token_type == TokenType.SYMBOL:
        if token == "<":
            token = "&lt;"
        if token == "&":
            token = "&amp;"
        if token == ">":
            token = "&gt;"
        outfile.write(f"<symbol> {token} </symbol>\n")

    if token_type == TokenType.STRING_CONST:
        outfile.write(f"<stringConstant> {token} </stringConstant>\n")

    if token_type == TokenType.INT_CONST:
        outfile.write(f"<integerConstant> {token} </integerConstant>\n")

    if token_type == TokenType.IDENTIFIER:
        outfile.write(f"<identifier> {token} </identifier>\n")


outfile.write("</tokens>\n")
outfile.close()
