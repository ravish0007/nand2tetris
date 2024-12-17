#!/usr/bin/python
import sys
from parser import Parser, Command
from code_writer import CodeWriter

if len(sys.argv) != 2:
    print('pass filepath only as arguement')


file_path = sys.argv[1]
outputfile = file_path.split('/')[-1].rstrip('.vm')

writer = CodeWriter(outputfile)

vm_parser = Parser(file_path)


while vm_parser.hasMoreLines():
    vm_parser.advance()
    if vm_parser.commandType() == Command.C_PUSH:
        writer.writePushPop('push', vm_parser.arg1(), vm_parser.arg2())
    elif  vm_parser.commandType() == Command.C_POP:
        writer.writePushPop('pop', vm_parser.arg1(), vm_parser.arg2())
    elif vm_parser.commandType() == Command.C_ARITHMETIC:
        writer.writeArithmetic(vm_parser.arg1())


writer.writeEnd()
writer.close()






