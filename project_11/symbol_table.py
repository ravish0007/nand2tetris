from enum import Enum


class ClassSymbolType(Enum):
    STATIC = "static"
    FIELD = "field"


class SubroutineSymbolType(Enum):
    VAR = "var"
    ARG = "arg"


class ClassSymbolTable:

    def __init__(self, class_name):
        self.class_name = class_name
        self.symbols = {}
        self.static_symbols_count = 0
        self.field_symbols_count = 0

    def add_entry(self, _type, name, var_type):
        if _type == ClassSymbolType.FIELD:
            self.symbols[name] = (
                ClassSymbolType.FIELD,
                var_type,
                self.field_symbols_count,
            )
            self.field_symbols_count += 1

        elif _type == ClassSymbolType.STATIC:
            self.symbols[name] = (
                ClassSymbolType.STATIC,
                var_type,
                self.field_symbols_count,
            )
            self.static_symbols_count += 1

    def get_symbol(self, name):
        if name in self.symbols:
            return self.symbols[name]
        return None

    def __str__(self):
        return f"""
        -----------------
        class name -> {self.class_name}
        static symbols -> {self.static_symbols_count}
        field symbols -> {self.field_symbols_count}
        symbols,
        {'\n'.join(f'{x} -> {self.symbols[x]}' for x in self.symbols)}
        -----------------
        """


class SubroutineTable:
    def __init__(self, name, subroutine_type, return_type, jack_class):
        self.name = name
        self.jack_class = jack_class
        self.subroutine_type = subroutine_type
        self.return_type = return_type

        self.symbols = dict()
        self.arg_symbols_count = 0
        self.var_symbols_count = 0

        if subroutine_type == "method":
            self.add_entry(SubroutineSymbolType.ARG, "this", self.jack_class.class_name)

    def add_entry(self, _type, name, var_type):
        if _type == SubroutineSymbolType.ARG:
            self.symbols[name] = (
                SubroutineSymbolType.ARG,
                var_type,
                self.arg_symbols_count,
            )
            self.arg_symbols_count += 1

        elif _type == SubroutineSymbolType.VAR:
            self.symbols[name] = (
                SubroutineSymbolType.VAR,
                var_type,
                self.var_symbols_count,
            )
            self.var_symbols_count += 1

    def get_symbol(self, name):
        symbol = self.symbols.get(name)
        if symbol is not None:
            return symbol

        return self.jack_class.get_symbol(name)

    def __str__(self):
        return f"""
        -----------------
        name -> {self.name}
        type -> {self.subroutine_type}
        arg symbols -> {self.arg_symbols_count}
        var symbols -> {self.var_symbols_count}
        symbols,
        {'\n'.join(f'{x} -> {self.symbols[x]}' for x in self.symbols)}
        -----------------
        """
