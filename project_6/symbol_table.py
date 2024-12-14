class SymbolTable:
    def __init__(self):
        self._freememory = 16
        self._labelcounter = 0
        self._table = {
                "SP": 0,
                "LCL": 1,
                "ARG": 2,
                "THIS": 3,
                "THAT": 4,
                "R0": 0,
                "R1": 1,
                "R2": 2,
                "R3": 3,
                "R4": 4,
                "R5": 5,
                "R6": 6,
                "R7": 7,
                "R8": 8,
                "R9": 9,
                "R10": 10,
                "R11": 11,
                "R12": 12,
                "R13": 13,
                "R14": 14,
                "R15": 15,
                "SCREEN": 16384,
                "KBD": 24576
                } 
    
    def add_label(self, symbol):
        if symbol in self._table:
            raise Exception(f'label {symbol} already defined')
        self._table[symbol] = self._labelcounter

    def increment_label_counter(self):
        self._labelcounter += 1

    def add_variable(self, symbol):
        if symbol not in self._table:
            self._table[symbol] = self._freememory
            self._freememory += 1
    
    def contains(self, symbol):
        return symbol in self._table

    def get_address(self, symbol):
        self.add_variable(symbol)
        return self._table[symbol]

