class Parser:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.comp_dict = {
                "0": "0101010",
                "1": "0111111",
                "-1": "0111010",
                "D": "0001100",
                "A": "0110000",
                "!D": "0001101",
                "!A": "0110001",
                "-D": "0001111",
                "-A": "0110011",
                "D+1": "0011111",
                "1+D": "0011111",
                "A+1": "0110111",
                "1+A": "0110111",
                "D-1": "0001110",
                "A-1": "0110010",
                "D+A": "0000010",
                "A+D": "0000010",
                "D-A": "0010011",
                "A-D": "0000111",
                "D&A": "0000000",
                "A&D": "0000000",
                "D|A": "0010101",
                "A|D": "0010101",

                "M": "1110000",
                "!M": "1110001",
                "-M": "1110011",
                "M+1": "1110111",
                "1+M": "1110111",
                "M-1": "1110010",
                "D+M": "1000010",
                "M+D": "1000010",
                "D-M": "1010011",
                "M-D": "1000111",
                "D&M": "1000000",
                "M&D": "1000000",
                "D|M": "1010101",
                "M|D": "1010101"
                }
        self.dest_dict = {
                "null": "000",
                "M": "001",
                "D": "010",
                "MD": "011",
                "DM": "011",
                "A": "100",
                "AM": "101",
                "MA": "101",
                "AD": "110",
                "DA": "110",
                "AMD": "111",
                "ADM": "111",
                "MAD": "111",
                "MDA": "111",
                "DAM": "111",
                "DMA": "111"
                }
        self.jump_dict = {
                "null": "000",
                "JGT": "001",
                "JEQ": "010",
                "JGE": "011",
                "JLT": "100",
                "JNE": "101",
                "JLE": "110",
                "JMP": "111"
                }
        
        self.prefixA = '0'
        self.prefixC = '111'


    def comp_lookup(self, token):
        return self.comp_dict.get(token, self.comp_dict['0'])

    def dest_lookup(self, token):
        return self.dest_dict.get(token, self.comp_dict['null'])

    def jump_lookup(self, token):
        return self.jump_dict.get(token, self.comp_dict['null'])

    def parse_A_instruction(self, instruction):
        get_binary = lambda x: bin(int(x))[2:].zfill(15)
        if instruction.isnumeric():
            return self.prefixA + get_binary(instruction)
        else:
            if instruction[0].isnumeric() and any(map(lambda x: x.isalpha(), instruction[1:])):
                raise Exception(f'Invalid A instruction {instruction}')
            else:
                return self.prefixA + get_binary(self.symbol_table.get_address(instruction))


    def parse_C_instruction(self, instruction):
        e = instruction.find('=')
        sc = instruction.find(';')

        dest =  'null' if e == -1 else instruction[0:e]
        comp =  instruction[e+1:] if sc == -1 else instruction[e+1:sc]
        jump = 'null' if sc == -1 else instruction[sc+1:]

        return self.prefixC + self.comp_dict[comp] + self.dest_dict[dest]  + self.jump_dict[jump]


    def parse_instruction(self, instruction):
        return self.parse_A_instruction(instruction[1:]) if instruction.startswith('@') else self.parse_C_instruction(instruction)

        
