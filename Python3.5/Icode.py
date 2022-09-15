from misc import *


class Quadruple:
    def __init__(self, op, arg1, arg2, result):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    def __repr__(self):
        if self.op == ASSIGNOP:
            # (:=, arg1, _, result)
            rep = '@' + str(self.result) + ' := @' + str(self.arg1)
        elif self.op in ['+', '-', '*', '/', MOD]:
            ## (op, arg1, arg2, result)
            rep = '@' + str(self.result) + ' := @' + str(self.arg1) + \
                ' ' + str(self.op) + ' @' + str(self.arg2)

        elif self.op == GOTO:
            ## (goto, _, _, result)
            rep = 'goto ' + str(self.result)
        elif self.op in [GE, GT,  NE, LE, LT, EQ]:
            ## (relop, arg1, arg2, result)
            rep = 'if @' + str(self.arg1) + ' ' + str(self.op) + \
                ' @' + str(self.arg2) + ' goto ' + str(self.result)
        elif self.op == PRINT:
            ## (print, _, _, _)
            rep = 'print @' + str(self.result)
        elif self.op == HALT:
            ## (halt, _, _, _)
            rep = 'halt'
        else:
            rep = 'quadruplet non reconnu'
        return rep


class Icode:
    def __init__(self):
        self.quadtab = []

    def run(self, symbtab):
        index = 0
        while 1:
            q = self.quadtab[index]
            if q.op == ASSIGNOP:
                val = symbtab.getvalue(q.arg1)
                if val == None:
                    raise RuntimeError("expression sans valeur")
                else:
                    symbtab.setvalue(q.result, val)
                index += 1
            elif q.op in ['+', '-', '*', '/', MOD]:
                arg1 = symbtab.getvalue(q.arg1)
                arg2 = symbtab.getvalue(q.arg2)
                if None in [arg1, arg2]:
                    raise RuntimeError("expression sans valeur")
                elif q.op == '+':
                    symbtab.setvalue(q.result, arg1+arg2)
                elif q.op == '-':
                    symbtab.setvalue(q.result, arg1-arg2)
                elif q.op == '*':
                    symbtab.setvalue(q.result, arg1*arg2)
                elif q.op == '/':
                    symbtab.setvalue(q.result, arg1/arg2)
                else:
                    symbtab.setvalue(q.result, arg1 % arg2)
                index += 1
            elif q.op == GOTO:
                index = q.result
            elif q.op in [GE, GT, EQ, NE, LE, LT]:
                arg1 = symbtab.getvalue(q.arg1)
                arg2 = symbtab.getvalue(q.arg2)
                if None in [arg1, arg2]:
                    raise RuntimeError("expression sans valeur")
                elif q.op == GE:
                    if arg1 >= arg2:
                        index = q.result
                    else:
                        index += 1
                elif q.op == GT:
                    if arg1 > arg2:
                        index = q.result
                    else:
                        index += 1
                elif q.op == EQ:
                    if arg1 == arg2:
                        index = q.result
                    else:
                        index += 1
                elif q.op == NE:
                    if arg1 != arg2:
                        index = q.result
                    else:
                        index += 1
                elif q.op == LE:
                    if arg1 <= arg2:
                        index = q.result
                    else:
                        index += 1
                elif q.op == LT:
                    if arg1 < arg2:
                        index = q.result
                    else:
                        index += 1
            elif q.op == PRINT:
                arg = symbtab.getvalue(q.result)
                if arg == None:
                    raise RuntimeError("expression sans valeur")
                else:
                    print('===> ' + str(arg))
                index += 1
            elif q.op == HALT:
                break
            else:
                raise RuntimeError("quadruplet non reconnu")

    def __repr__(self):
        p = 0
        rep = ""
        for e in self.quadtab:
            rep = rep + str(p) + ': ' + str(e)
            p += 1
            if p < len(self.quadtab):
                rep += '\n'
        return rep

    def emit(self, op, arg1, arg2, result):
        self.quadtab.append(Quadruple(op, arg1, arg2, result))

    def fillgoto(self, L, q):
        for i in L:
            self.quadtab[i].result = q

    def nextquad(self):
        return len(self.quadtab)
