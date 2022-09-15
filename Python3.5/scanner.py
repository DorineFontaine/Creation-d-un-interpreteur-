from string import ascii_letters, digits
import readline
from symbtab import *
from misc import *
from sys import argv, stderr


class LexicalError(SyntaxError):
    "Sert a indiquer une erreur lexicale"


class CompilerError(SyntaxError):
    "Sert a indiquer une erreur du compilateur"

# Analyse lexicale:


class Scanner:
    "Effectue l'analyse lexicale."

    def __init__(self, symbtab, f):
        self.symbtab = symbtab
        self.f = f  # fichier ou se trouve le code source
        self.lineno = 1

    def fail(self):
        "Branchement sur l'etat initial du prochain automate."
        # si on insere un nouvelle automate il faut modifier fail en consequence
        # car on passe par fail pour passer d'automate en automate
        if self.start == 0:
            self.start = 3
        elif self.start == 3:
            self.start = 6
        elif self.start == 6:
            self.start = 11

        elif self.start == 11:
            self.start = 13

        elif self.start == 13:
            self.start = 16

        elif self.start == 16:  # l'etat final

            raise LexicalError("ligne " + str(self.lineno))
        else:
            raise CompilerError("ligne " + str(self.lineno))
        return self.start

    def nexttoken(self):
        "Simule les mouvements d'un automate."
        self.start = 0
        state = 0
        pos = 0  # sert a repositionner la tete de lecture en cas de recul
        lexbuf = ""
        while 1:
            # espaces:
            if state == 0:
                c = self.f.read(1)  # lecture d'un caractere dans f
                if c == '':
                    return (EOF, None)  # on est arrive a la fin du fichier
                elif c in ' \t':
                    pass
                elif c in '\n':
                    self.lineno += 1
                elif c in '#':
                    self.f.readline()  # on fait sauter le commentaire, on ne prend pas en compte
                else:
                    state = self.fail()
            # id:
            elif state == 3:
                if c in ascii_letters:  # si c'est une lettre
                    lexbuf = lexbuf + c
                    state = 4
                else:
                    state = self.fail()
            elif state == 4:
                pos = self.f.tell()  # tell renvoie la position actuelle dans le fichier
                c = self.f.read(1)
                if c in ascii_letters or c in digits:  # si c'est une lettre ou un nombre
                    lexbuf = lexbuf + c
                else:
                    state = 5
            elif state == 5:
                self.f.seek(pos, 0)  # recule la tete de lecture
                if lexbuf == PRINT:
                    return(PRINT, None)

                else:
                    p = self.symbtab.insert(lexbuf, ID)
                    return (self.symbtab.gettoken(p), p)
            # num:
            elif state == 6:
                if c in digits:  # si c'est un nombre
                    lexbuf = lexbuf + c
                    state = 7
                else:
                    state = self.fail()  # retour a l'état initial
            elif state == 7:
                pos = self.f.tell()
                c = self.f.read(1)
                if c in digits:
                    lexbuf = lexbuf + c  # si c'est un nombre
                elif c == '.':
                    state = 8  # si c'est un . on va à l'etat 8
                else:
                    state = 10  # si c'est une lettre ou autre caractere on passe à l'etat 10
            elif state == 8:
                c = self.f.read(1)
                if c in digits:  # si c'est un nombre
                    lexbuf = lexbuf + '.' + c
                    state = 9
                else:
                    raise LexicalError("ligne " + str(self.lineno))
            elif state == 9:
                pos = self.f.tell()
                c = self.f.read(1)
                if c in digits:
                    lexbuf = lexbuf + c  # si c'est un nombre
                else:
                    state = 10  # tout autre chose qu'on nomme
            elif state == 10:
                self.f.seek(pos, 0)  # recule la tete de lecture
                p = self.symbtab.insert(lexbuf, NUM)
                self.symbtab.setvalue(p, int(lexbuf))
                return (self.symbtab.gettoken(p), p)

            # assignop
            elif state == 11:
                if c == ':':
                    state = 12
                else:
                    # renvoie la valeur pour la tester pour un autre automate à l'etat initial
                    state = self.fail()

            elif state == 12:
                c = self.f.read(1)
                if c == '=':
                    return (ASSIGNOP, None)
                else:
                    # on autorise pas d'avoir : sans = a la suite
                    raise LexicalError("ligne " + str(self.lineno))

             # relop
            # NE,GE,LE

            elif state == 13:
                if c == '<':
                    state = 15
                elif c == ">":
                    state = 14
                elif c == "=":
                    return(RELOP, EQ)
                else:
                    state = self.fail()  # envoie directement en état finale

            elif state == 15:
                pos = self.f.tell()
                c = self.f.read(1)
                if c == ">":
                    return(RELOP, NE)
                elif c == "=":
                    return(RELOP, LE)
                else:
                    self.f.seek(pos, 0)
                    return(RELOP, LT)

            elif state == 14:
                pos = self.f.tell()
                c = self.f.read(1)
                if c == "=":
                    return(RELOP, GE)
                else:
                    self.f.seek(pos, 0)
                    return(RELOP, GT)

            # autre:
            elif state == 16:

                if c in ';+-*/()':
                    return (c, None)
                else:
                    state = self.fail()
            # erreur:
            else:
                raise CompilerError("ligne " + str(self.lineno))


if __name__ == "__main__":
    if len(argv) != 2:
        stderr.write("usage: python parser.py <file>\n")
    else:
        with open(argv[1], 'r') as f:
            symbtab = Symbtab()
            scanner = Scanner(symbtab, f)

            print(symbtab)
