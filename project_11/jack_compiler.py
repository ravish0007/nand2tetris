#!/usr/bin/python
import sys
import os

from jack_tokenizer import Tokenizer, TokenType
from compilation_engine import CompilationEngine
from vm_writer import VMWriter


if len(sys.argv) != 2:
    print("pass filepath only as arguement")


def compile_file(file_path):
    tokenizer = Tokenizer(file_path)
    vm_file = file.split("/")[-1].rstrip(".jack") + ".vm"
    vm_writer = VMWriter(vm_file)
    compiler = CompilationEngine(tokenizer, vm_writer)
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
    compile_file(file)
