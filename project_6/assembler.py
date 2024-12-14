#!/usr/bin/python

import sys
from parser import Parser
from symbol_table import SymbolTable
from collections import deque


symbol_table = SymbolTable()
parser = Parser(symbol_table)

filepath = sys.argv[1]
outputpath = filepath.split('/')[-1][:-4] + '.hack'
outfile = open(outputpath, 'w')
 
queue_a = deque()
queue_b = deque()

def clean_comments():
    lines = open(filepath).readlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('//'):
            continue
        elif line.find('//') > 0:
            line = line[0: line.find('//')].strip()
            queue_a.append(line)
        else:
            queue_a.append(line)


def first_pass():
    while queue_a:
        line = queue_a.popleft()
        if line.startswith('(') and line.endswith(')'):
            label = line[1:-1]
            symbol_table.add_label(label)
            continue
        else:
            symbol_table.increment_label_counter()  
        queue_b.append(line);

def second_pass():
    while queue_b:
        line = queue_b.popleft()
        bin_inst  = parser.parse_instruction(line)
        outfile.write(bin_inst+'\n')

    outfile.close()


clean_comments()
first_pass()
second_pass()

