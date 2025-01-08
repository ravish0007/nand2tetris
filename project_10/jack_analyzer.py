#!/usr/bin/python
import sys

from jack_tokenizer import Tokenizer, TokenType

from jack_compiler import Compiler

file = sys.argv[1]
outputfile_name = sys.argv[1].split("/")[-1][:-5] + ".xml"


outfile = open(outputfile_name, "w")
outfile.write("<tokens>\n")


tokenizer = Tokenizer(file)
compiler = Compiler(tokenizer)

compiler.compileClass()
