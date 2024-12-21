#!/usr/bin/python
import sys
from parser import Parser, Command
from code_writer import CodeWriter
import os

if len(sys.argv) != 2:
    print("pass filepath only as arguement")


def translate_file(file_path, writer):
    vm_parser = Parser(file_path)
    while vm_parser.hasMoreLines():
        vm_parser.advance()
        command_type = vm_parser.commandType()
        if command_type == Command.C_PUSH:
            writer.writePushPop("push", vm_parser.arg1(), vm_parser.arg2())
        elif command_type == Command.C_POP:
            writer.writePushPop("pop", vm_parser.arg1(), vm_parser.arg2())
        elif command_type == Command.C_LABEL:
            writer.writeLabel(vm_parser.arg1())
        elif command_type == Command.C_GOTO:
            writer.writeGoto(vm_parser.arg1())
        elif command_type == Command.C_IF:
            writer.writeIf(vm_parser.arg1())
        elif command_type == Command.C_ARITHMETIC:
            writer.writeArithmetic(vm_parser.arg1())
        elif command_type == Command.C_FUNCTION:
            writer.writeFunction(vm_parser.arg1(), vm_parser.arg2())
        elif command_type == Command.C_CALL:
            writer.writeCall(vm_parser.arg1(), vm_parser.arg2())
        elif command_type == Command.C_RETURN:
            writer.writeReturn()


path = sys.argv[1]
if path == ".":
    path = os.path.abspath(".")

if os.path.isdir(path):
    vm_files = filter(lambda x: x.endswith(".vm"), os.listdir(path))
    files = list(map(lambda x: os.path.join(path, x), vm_files))
else:
    files = [path]

outputfile = path.split("/")[-1].rstrip(".vm")
writer = CodeWriter(outputfile)

if len(files) > 1:
    writer.bootstrap()

for file in files:
    writer.setFileName(file.split("/")[-1].rstrip(".vm"))
    translate_file(file, writer)


writer.writeEnd()
writer.close()
