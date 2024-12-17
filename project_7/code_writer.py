

def generate_assembly_output(tip, commands):
     return '\n'.join([f'// {tip}', *commands, '', ''])

def generate_end():
    return generate_assembly_output('reached end', ['(END)', '@END', '0;JMP'])

def generate_unary_arithmetic(type):
    operation_type = {
            'neg': 'M=-M',
            'not': 'M=!M'
    }
    commands = [ '@SP', 'A=M-1', operation_type[type]]
    return generate_assembly_output(type, commands)


def generate_binary_arithmetic(type):
    operation_type = {
            'add': 'M=M+D',
            'sub': 'M=M-D',
            'or': 'M=M|D',
            'and': 'M=M&D'
    }
    commands = [ '@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', operation_type[type]]
    return generate_assembly_output(type, commands)

def generate_comparision(type, label):
    operation_type = {
            'eq': 'D;JEQ',
            'lt': 'D;JLT',
            'gt': 'D;JGT'

            }
    commands = [  '@SP',
                 'AM=M-1',
                 'D=M',
                 '@SP',
                 'A=M-1',
                 'D=M-D',
                 f'@jumptrue{label}',
                 operation_type[type],
                 'D=0',
                 f'@jumpfalse{label}',
                 '0;JMP',
                 f'(jumptrue{label})',
                 'D=-1',
                 f'(jumpfalse{label})',
                 '@SP',
                 'A=M-1'
                 'M=D',
                ]
    return generate_assembly_output(type, commands)


def generate_push(segment, index, label):
    location_mapping = {
         'this': 'THIS',
         'that': 'THAT',
         'argument': 'ARG',
         'local': 'LCL',
         'pointer': '3',
         'temp': '5'
    }

    push_type = {
            'static': [ f"@{label}.{index}", "D=M"],
            'constant': [ f'@{index}', 'D=A' ],
            'rest': [ f'@{location_mapping.get(segment, "ERRRORRRR")}', 'D=M', f'@{index}', 'A=D+A', 'D=M' ]
    }
    commands = [ *push_type.get(segment, push_type['rest']), '@SP', 'A=M', 'M=D', '@SP', 'M=M+1' ]
    return generate_assembly_output(segment, commands)


def generate_pop(segment, index, label):


    if segment == 'static':
        return generate_assembly_output(f'pop {segment} {index}', [f'@{label}.{index}', 'D=M', '@SP', 'A=M', 'M=D', '@SP' 'M=M+1'])

    location_mapping = {
         'this': 'THIS',
         'that': 'THAT',
         'argument': 'ARG',
         'local': 'LCL',
         'pointer': '3',
         'temp': '5'
    }

    commands = [
               f'@{location_mapping[segment]}',
               'D=A',
               f'@{index}',
               'D=M+D',
               '@R13',
               'M=D',
               '@SP',
               'AM=M-1',
               'D=M',
               '@R13',
               'A=M',
               'M=D'
            ]

    return generate_assembly_output(f'pop {segment} {index}', commands)



class CodeWriter:
    def __init__(self, output):
        self.static_label = output
        self.file = open(output+'.asm', 'w')
        self.label = 0

    def close(self):
        self.file.close()

    def writeArithmetic(self, command):
        if command in {'add', 'sub', 'or', 'and'}:
            self.file.write(generate_binary_arithmetic(command))
        elif command in {'neg', 'not'}:
            self.file.write(generate_unary_arithmetic(command))
        elif command in {'eq', 'gt', 'lt'}:
            self.file.write(generate_comparision(command, self.label))
            self.label += 1

    def writePushPop(self, command_type, segment, index):
        if command_type == 'push':
           self.file.write(generate_push(segment, index, self.static_label))
        elif command_type == 'pop':
            self.file.write(generate_pop(segment, index, self.static_label))
 

    def writeEnd(self):
        self.file.write(generate_end())

