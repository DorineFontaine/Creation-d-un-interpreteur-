from sys import argv, stderr
from Icode import *

from misc import *
from symbtab import *
from scanner import *


class Parser:
    "Analyse syntaxique."

    def __init__(self, scanner, symbtab):
        self.scanner = scanner
        self.symbtab = symbtab
        self.Icode = Icode()

    def match(self, token):
        if self.lookahead == token:
            (self.lookahead, self.tokenat) = self.scanner.nexttoken()
            #print(self.lookahead, self.tokenat)

        else:
            error_msg = "ligne " + \
                str(self.scanner.lineno) + ", " + str(token) + " attendu"
            raise SyntaxError(error_msg)

    def parse(self):
        (self.lookahead, self.tokenat) = self.scanner.nexttoken()
        #print(self.lookahead, self.tokenat)
        self.L()

        print("OK")
        print(self.symbtab)

    def L(self):
        "L->I;L|eof"

        if self.lookahead == ID or self.lookahead == PRINT:
            self.I()
            self.match(';')
            self.L()

        else:
            self.match(EOF)
            self.Icode.emit(HALT, None, None, None)

    def I(self):
        "I->id:=E|print(E)"

        if self.lookahead == ID:
            id_adresse = self.tokenat
            self.match(ID)
            self.match(ASSIGNOP)
            E_adresse = self.E()
            self.Icode.emit(ASSIGNOP, E_adresse, None, id_adresse)

        elif self.lookahead == PRINT:
            self.match(PRINT)
            self.match("(")
            E_adresse = self.E()
            self.match(")")
            self.Icode.emit(PRINT, None, None, E_adresse)

    def E(self):
        "E->F+E1 |F-E1|F "
        f_adresse = self.F()
        if self.lookahead == '+':
            self.match('+')
            E1_adresse = self.E()
            E_adresse = self.symbtab.newid()
            self.Icode.emit("+", f_adresse, E1_adresse, E_adresse)
            return E_adresse
        else:
            return f_adresse

    def F(self):
        "F->(E)|num|id"

        if self.lookahead == '(':
            self.match('(')
            self.E()
            self.match(')')

        elif self.lookahead == NUM:
            num_adresse = self.tokenat
            self.match(NUM)
            return num_adresse

        elif self.lookahead == ID:
            id_adresse = self.tokenat
            self.match(ID)
            return id_adresse

        else:
            error_msg = "ligne " + \
                str(self.scanner.lineno) + " : '(', NUM ou ID attendu"
            raise SyntaxError(error_msg)


# Programme principal :
if __name__ == "__main__":
    if len(argv) != 2:
        stderr.write("usage: python parser.py <file>\n")
    else:
        with open(argv[1], 'r') as f:
            symbtab = Symbtab()
            scanner = Scanner(symbtab, f)
            parser = Parser(scanner, symbtab)
            parser.parse()
            print(parser.Icode)
            print("#####")
            parser.Icode.run(parser.symbtab)
            print("#####")
            print(parser.symbtab)
