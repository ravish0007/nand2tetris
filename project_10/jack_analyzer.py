#!/usr/bin/python
import sys
import os

from jack_tokenizer import Tokenizer, TokenType
from jack_compiler import Compiler


if len(sys.argv) != 2:
    print("pass filepath only as arguement")


def compile_file(file_path, tokenizer):
    compiler = Compiler(tokenizer, file_path)
    compiler.compileClass()


path = sys.argv[1]
if path == ".":
    path = os.path.abspath(".")

if os.path.isdir(path):
    program_files = filter(lambda x: x.endswith(".jack"), os.listdir(path))
    files = list(map(lambda x: os.path.join(path, x), program_files))
else:
    files = [path]

for file in files:
    tokenizer = Tokenizer(file)
    compile_file(file.split("/")[-1].rstrip(".jack"), tokenizer)
