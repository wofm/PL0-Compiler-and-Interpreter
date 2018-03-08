class Pcode:
    LIT = 0
    OPR = 1
    LOD = 2
    STO = 3
    CAL = 4
    INT = 5
    JMP = 6
    JPC = 7
    pcode = ["LIT", "OPR", "LOD", "STO", "CAL", "INT", "JMP", "JPC"]

    def __init__(self, f, l, a):
        self.f = f
        self.l = l
        self.a = a
