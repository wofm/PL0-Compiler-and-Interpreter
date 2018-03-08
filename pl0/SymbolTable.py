class SymbolTable:
    tableMax = 100  # 符号表大小
    symMax = 10  # 符号的最大长度
    addrMax = 1000000  # 最大允许的数值
    levMax = 3  # 最大允许过程嵌套声明层数[0, levmax]
    numMax = 14  # number的最大位数
    tableswitch = True  # 显示名字表与否

    class Item:
        constant = 0
        variable = 1
        procedure = 2

        def __init__(self, type, value, lev, addr, size):
            self.name = ""
            self.type = type
            self.value = value
            self.lev = lev
            self.addr = addr
            self.size = size

    def __init__(self):
        self.table = list()  # 符号表
        for i in range(SymbolTable.tableMax):
            self.table.append(SymbolTable.Item(0, 0, 0, 0, 0))  # 首项为空,初始化
        self.tablePtr = 0  # 当前表项指针

    def get(self, i):  # 得到符号表元素
        # if (len(self.table) <= i):
        #     self.table.append(SymbolTable.Item(0, 0, 0, 0, 0))
        return self.table[i]

    '''
    把把某个符号登录到名字表中 名字表从1开始填，0表示不存在该项符号
    sym 要登记到名字表的符号
    type 该符号的类型：const,var,procedure
    lev 名字所在的层次
    dx 当前应分配的变量的相对地址，注意调用enter()后dx要加一
    num 变量的值，如果不是constant就为0
    '''

    def enter(self, sym, type, lev, dx, num):  # TODO 以后要改
        self.tablePtr += 1
        item = self.get(self.tablePtr)
        item.name = sym.value  # TODO 根据lex的返回修改
        item.type = type
        if type == SymbolTable.Item.constant:

            item.value = num  # TODO 根据lex的返回修改
        elif type == SymbolTable.Item.variable:
            item.lev = lev
            item.addr = dx
        elif type == SymbolTable.Item.procedure:
            item.lev = lev

    # 在名字表中查找某个名字的位置 查找符号表是从后往前查， 这样符合嵌套分程序名字定义和作用域的规定
    # idt 要查找的名字
    # 如果找到则返回名字项的下标，否则返回0
    def position(self, idt):
        for i in range(len(self.table) - 1, 0, -1):
            if self.table[i].name == idt:
                return i
        return 0

    def printself(self):
        print(self.table)

    def debugTable(self, tx0):
        return 1
