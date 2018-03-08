import Err
import Interpreter
import Pcode
import SymbolTable
import word_anay

FUNC = {
    'PLUS': 2,
    'MINUS': 3,
    'TIMES': 4,
    'DIVIDE': 5,
    'NUMBER': 7,
    'EQUAL': 8,
    'UNEQUAL': 9,
    'LESS': 10,
    'MOE': 11,
    'MORE': 12,
    'LORE': 13
}


class Praser:
    def __init__(self, input, out_file):  # input是输入字符串,outfile是输出的文件
        self.lex = word_anay.word_anay(input)  # 词法分析器
        self.line = 1  # 初始行数
        self.nextsym()  # 符号

        self.table = SymbolTable.SymbolTable()  # 符号表
        self.interp = Interpreter.Interpreter(out_file)
        self.myErr = Err.Err(out_file)  # 错误处理
        self.declbegsys = set()
        self.declbegsys.add('CONST')
        self.declbegsys.add('VAR')
        self.declbegsys.add('PROCEDURE')
        # 表示申明开始的符号集合：声明的FIRST集合


        self.statbegsys = set()
        self.statbegsys.add('BEGIN')
        self.statbegsys.add('CALL')
        self.statbegsys.add('IF')
        self.statbegsys.add('WHILE')
        self.statbegsys.add('REPEAT')
        # 表示语句开始的符号集合：语句的FIRST集合

        self.facbegsys = set()  # 表示因子开始的符号集合：因子的FIRST集合
        self.facbegsys.add('ID')
        self.facbegsys.add('NUMBER')
        self.facbegsys.add('LPAREN')
        # 当前作用域的堆栈帧大小，或者说数据大小(datasize)
        # 计算每个变量在运行栈中相对本过程基地址的偏移量
        # 放在symbolTable中的address域
        # 生成目标代码时再放在code中的a域
        self.dx = 0

    def nextsym(self):  # 得到下一个单词
        # line=self.sym.lineno

        self.sym = self.lex.getsym()
        if not self.sym:
            msg = "在第" + str(self.line) + "行缺少语法成分"
            raise Exception(msg)
        self.line = self.sym.lineno


        # 测试当前符号是否合法 本过程有三个参数，s1、s2为两个符号集合，n为出错代码。
        # 本过程的功能是：测试当前符号（即sym变量中的值）是否在s1集合中， 如果不在，就通过调用出错报告过程输出出错代码n，
        # 并放弃当前符号，通过词法分析过程获取一下单词， 直到这个单词出现在s1或s2集合中为止。 这个过程在实际使用中很灵活，主要有两个用法：
        # 在进入某个语法单位时，调用本过程， 检查当前符号是否属于该语法单位的开始符号集合。 若不属于，则滤去开始符号和后继符号集合外的所有符号。
        # 在语法单位分析结束时，调用本过程， 检查当前符号是否属于调用该语法单位时应有的后继符号集合。 若不属于，则滤去后继符号和开始符号集合外的所有符号。
        # 通过这样的机制，可以在源程序出现错误时， 及时跳过出错的部分，保证语法分析可以继续下去。
        # firstSet 需要的符号
        # followSet 不需要的符号，添加一个补救集合
        # errcode 错误号

    def test(self, s1, s2, errcode):
        if self.sym.type in s1 is False:
            self.myErr.report(errcode, self.sym.lineno)
            s1 = s1 | s2
            while self.sym.type in s1 == False:
                self.nextsym()

    # < 程序 >::= < 分程序 >.启动语法分析过程，此前必须先调用一次nextsym()
    def Parse(self):
        # print(type(self.sym))
        nxtlev = set()
        nxtlev |= self.declbegsys
        nxtlev |= self.statbegsys
        nxtlev.add('DOT')

        #
        #   <程序> ::= <分程序>. FOLLOW(block)={ . }
        #   <分程序> ::= [<常量说明部分>][变量说明部分>]{<过程说明部分>}<语句>
        #   FIRST(declaration)={const var procedure null };
        #   <语句> ::= <赋值语句>|<条件语句>|<当型循环语句>|<过程调用语句>|<读语句>|<写语句>|<复合语句>|<空>
        #   FIRST(statement)={begin call if while repeat null };
        #   FIRST(block)=  {const var procedure begin call if while repeat  . }
        #

        self.block(0, nxtlev)  # 解析<分程序>

        if self.sym.type != 'DOT':
            self.myErr.report(9, self.sym.lineno)
            try:
                self.interp.debugPcodeArray()
            except Exception:
                print("***write pcode Array to file meet with error***")

    #
    #   分析-->分程序
    #   <分程序>：=[<常数说明部分>][<变量说明部分>]{<过程说明部分>}<语句>
    #
    #   @param lev 当前分程序所在层
    #   @param fsys 当前模块的FOLLOW集合
    #

    def block(self, lev, fsys):
        nxtlev = set()
        dx0 = self.dx  # 记录本层之前的数据量, 以便返回时恢复
        tx0 = self.table.tablePtr  # 记录本层名字的初始位置
        cx0 = 0
        # 置初始值为3的原因是：
        # 每一层最开始的位置有三个空间用于存放静态链SL、动态链DL和返回地址RA
        self.dx = 3
        # 当前pcode代码的地址，传给当前符号表的addr项

        self.table.get(self.table.tablePtr).addr = self.interp.arrayPtr
        self.interp.gen(Pcode.Pcode.JMP, 0, 0)
        if lev > SymbolTable.SymbolTable.levMax:
            self.myErr.report(32, self.sym.lineno)
        # 分析 < 说明部分 >
        # print(type(self.sym))
        while True:
            # < 常量说明部分 >::= const < 常量定义 > {, < 常量定义 >};
            if self.sym.type == 'CONST':
                self.nextsym()
                self.constdeclaration(lev)

                while self.sym.type == 'DOU':
                    self.nextsym()
                    self.constdeclaration(lev)
                if self.sym.type == 'PAR':  # 如果是分号，表示常量申明结束
                    self.nextsym()
                else:
                    self.myErr.report(5, self.sym.lineno)  # 漏了逗号或者分号

            # <变量说明部分>
            # var<标识符>{,<标识符>}
            if self.sym.type == 'VAR':
                self.nextsym()
                self.vardeclaration(lev)  # 识别<标识符>
                while self.sym.type == 'DOU':
                    self.nextsym()
                    self.vardeclaration(lev)
                if self.sym.type == 'PAR':  # 如果是分号，表示变量申明结束
                    self.nextsym()
                else:
                    self.myErr.report(5, self.sym.lineno)

            # < 过程说明部分 >::=  procedure < 标识符 >; < 分程序 >;
            # FOLLOW(semicolon) = {NULL < 过程首部 >}，
            # 需要进行test procedure a1;
            # procedure 允许嵌套，故用while
            while self.sym.type == 'PROCEDURE':
                self.nextsym()
                if self.sym.type == 'ID':  # 填写符号表
                    self.table.enter(self.sym, SymbolTable.SymbolTable.Item.procedure, lev, self.dx, 0)
                    self.nextsym()
                else:
                    self.myErr.report(4, self.sym.lineno)
                if self.sym.type == 'PAR':  # 分号，表示<过程首部>结束
                    self.nextsym()
                else:
                    self.myErr.report(5, self.sym.lineno)  # 漏了逗号或者分号
                nxtlev = set(fsys)  # 当前模块(block)的FOLLOW集合
                nxtlev.add("PAR")
                self.block(lev + 1, nxtlev)  # 嵌套层次+1，分析分程序

                if self.sym.type == 'PAR':  # <过程说明部分> 识别成功
                    self.nextsym()
                    nxtlev = set(self.statbegsys)
                    nxtlev.add('ID')
                    nxtlev.add('PROCEDURE')
                    self.test(nxtlev, fsys, 6)  # 测试symtype属于FIRST(statement)
                else:
                    self.myErr.report(5, self.sym.lineno)  # 漏了逗号或者分号

            # FIRST(statement) = {begin call if while repeat null};
            # FIRST(declaration)={const var procedure null};
            # 一个分程序的说明部分识别结束后，下面可能是语句statement或者嵌套的procedure（first（block）={各种声明}）
            nxtlev = set(self.statbegsys)
            # FIRST(statement) = {ident}
            nxtlev.add('ID')
            self.test(nxtlev, self.declbegsys, 7)

            if (self.sym.type in self.declbegsys) is False:  # 直到没有声明符号
                break

        # 开始生成当前过程代码
        # 分程序声明部分完成后，即将进入语句的处理， 这时的代码分配指针cx的值正好指向语句的开始位置，
        # 这个位置正是前面的jmp指令需要跳转到的位置
        item = self.table.get(tx0)
        self.interp.pcodeArray[item.addr].a = self.interp.arrayPtr  # 过程入口地址填写在pcodeArray中的jmp 的第二个参数
        item.addr = self.interp.arrayPtr  # 当前过程代码地址
        item.size = self.dx  # dx:一个procedure中的变量数目+3 ，声明部分中每增加一条声明都会给dx+1

        # 声明部分已经结束，dx就是当前过程的堆栈帧大小
        # 于是通过前面记录下来的地址值，把这个jmp指令的跳转位置改成当前cx的位置。
        # 并在符号表中记录下当前的代码段分配地址和局部数据段要分配的大小（dx的值）。 生成一条int指令，分配dx个空间，
        # 作为这个分程序段的第一条指令。 下面就调用语句处理过程statement分析语句。
        cx0 = self.interp.arrayPtr
        # 生成分配内存代码
        self.interp.gen(Pcode.Pcode.INT, 0, self.dx)

        # 打印 < 说明部分 > 代码

        self.table.debugTable(tx0)

        # 分析 < 语句 >
        nxtlev = set(fsys)
        nxtlev.add('PAR')
        nxtlev.add('END')
        self.statement(nxtlev, lev)

        # 分析完成后，生成操作数为0的opr指令， 用于从分程序返回（对于0层的主程序来说，就是程序运行完成，退出）。
        self.interp.gen(Pcode.Pcode.OPR, 0, 0)  # 每个过程出口都要使用的释放数据段指令

        nxtlev = set()
        nxtlev.add('NUMBER')  # 分程序没有补救集合
        self.test(fsys, nxtlev, 8)  # 检测后跟符号正确性

        # self.interp.listcode(0)

        self.dx = dx0  # 恢复堆栈帧计数器
        self.table.tablePtr = tx0  # 回复名字表位置



        # 分析<常量定义>
        # <常量定义> ::= <标识符>=<无符号整数>
        # @param lev 当前所在的层次

    def constdeclaration(self, lev):
        if self.sym.type == 'ID':
            id = self.sym  # 先保存起来
            self.nextsym()
            if self.sym.type == 'EQUAL' or self.sym.type == 'GIVE':  # 等于或者赋值符号
                if self.sym.type == 'GIVE':
                    self.myErr.report(1, self.sym.lineno)
                self.nextsym()
                if self.sym.type == 'NUMBER':
                    self.table.enter(id, SymbolTable.SymbolTable.Item.constant, lev, self.dx,
                                     self.sym.value)  # 将常量填入符号表
                    self.nextsym()
                else:
                    self.myErr.report(2, self.sym.lineno)
            else:
                self.myErr.report(3, self.sym.lineno)
        else:
            self.myErr.report(4, self.sym.lineno)

            # 分析<标识符>
            # <变量说明部分>::= var <标识符> { , <标识符> } ;
            # @param lev 当前所在的层次

    def vardeclaration(self, lev):
        if self.sym.type == 'ID':
            # 填写名字表并改变堆栈帧计数器
            # 符号表中记录下标识符的名字、它所在的层及它在所在层中的偏移地址
            self.table.enter(self.sym, SymbolTable.SymbolTable.Item.variable, lev, self.dx, 0)
            # 变量定义过程中, 会用dx变量记录下局部数据段分配的空间个数
            self.dx += 1
            self.nextsym()
        else:
            self.myErr.report(4, self.sym.lineno)


            # 分析<语句>
            # @param fsys FOLLOW集合
            # @param lev 当前层次

    def statement(self, fsys, lev):
        # FIRST(statement) = {ident, read, write, call, if,while }
        if self.sym.type == 'ID':
            self.praseAssignStatement(fsys, lev)
        elif self.sym.type == 'READ':
            self.praseReadStatement(fsys, lev)
        elif self.sym.type == 'WRITE':
            self.praseWriteStatement(fsys, lev)
        elif self.sym.type == 'CALL':
            self.praseCallStatement(fsys, lev)
        elif self.sym.type == 'IF':
            self.praseIfStatement(fsys, lev)
        elif self.sym.type == 'BEGIN':
            self.praseBeginStatement(fsys, lev)
        elif self.sym.type == 'WHILE':
            self.praseWhileStatement(fsys, lev)
        elif self.sym.type == 'REPEAT':
            self.praseRepeatStatement(fsys, lev)
        else:
            nxlev = set()
            self.test(fsys, nxlev, 19)  # 语句后的符号不正确

    # 解析<重复语句> ::= repeat<语句>{;<语句>}until<条件>
    def praseRepeatStatement(self, fsys, lev):
        cx1 = self.interp.arrayPtr
        self.nextsym()
        nxtlev = set(fsys)
        nxtlev.add("PAR")
        nxtlev.add('UNTIL')
        self.statement(fsys, lev)
        while self.sym.type in self.statbegsys or self.sym.type == 'PAR':
            if self.sym.type == 'PAR':
                self.nextsym()
            else:
                self.myErr.report(34, self.sym.lineno)

            self.statement(nxtlev, lev)

        if self.sym.type == 'UNTIL':
            self.nextsym()
            self.condition(fsys, lev)
            self.interp.gen(Pcode.Pcode.JPC, 0, cx1)
            # TODO 被注释的else


            # 分析<当型循环语句>
            # <当型循环语句> ::= while<条件>do<语句>
            # 首先用cx1变量记下当前代码段分配位置， 作为循环的开始位置。 然后处理while语句中的条件表达式生成相应代码把结果放在数据栈顶，
            # 再用cx2变量记下当前位置， 生成条件转移指令， 转移位置未知，填0。 通过递归调用语句分析过程分析do语句后的语句或语句块并生成相应代码。
            # 最后生成一条无条件跳转指令jmp，跳转到cx1所指位置， 并把cx2所指的条件跳转指令JPC的跳转位置,改成当前代码段分配位置
            # @param fsys FOLLOW符号集
            # @param lev 当前层次

    def praseWhileStatement(self, fsys, lev):
        cx1 = self.interp.arrayPtr  # 保存判断条件操作的位置

        self.nextsym()
        nxtlev = set(fsys)
        # FOLLOW(条件)={ do }
        nxtlev.add('DO')
        self.condition(nxtlev, lev)  # 分析<条件>
        cx2 = self.interp.arrayPtr  # 保存循环体的结束下一个位置
        self.interp.gen(Pcode.Pcode.JPC, 0, 0)
        if self.sym.type == 'DO':
            self.nextsym()
        else:
            self.myErr.report(18, self.sym.lineno)
        self.statement(fsys, lev)  # 分析<语句>
        self.interp.gen(Pcode.Pcode.JMP, 0, cx1)  # 回头重新判断条件
        self.interp.pcodeArray[cx2].a = self.interp.arrayPtr  # 反填跳出循环的地址，与<条件语句>类似


        # 分析<复合语句>
        # <复合语句> ::= begin<语句>{;<语句>}end 通过循环遍历begin/end语句块中的每一个语句，
        # 通过递归调用语句分析过程分析并生成相应代码。
        #
        # @param fsys FOLLOW集合
        # @param lev当前层次

    def praseBeginStatement(self, fsys, lev):
        self.nextsym()

        nxtlev = set(fsys)
        # FOLLOW(statement)={ ; end }
        nxtlev.add('PAR')
        nxtlev.add('END')
        self.statement(nxtlev, lev)
        # 循环分析{;<语句>},直到下一个符号不是语句开始符号或者收到end
        while self.sym.type in self.statbegsys or self.sym.type == 'PAR':

            if self.sym.type == 'PAR':
                self.nextsym()
            else:
                self.myErr.report(10, self.sym.lineno)

            self.statement(nxtlev, lev)

        if self.sym.type == 'END':  # 若为end ，statement解析成功
            self.nextsym()
        else:
            self.myErr.report(17, self.sym.lineno)


            # 分析<条件语句>
            # <条件语句> ::= if <条件> then <语句>
            # 按if语句的语法，首先调用逻辑表达式处理过程， 处理if语句的条件，把相应的真假值放到数据栈顶。
            # 接下去记录下代码段分配位置（即下面生成的jpc指令的位置）， 然后生成条件转移jpc指令（遇0或遇假转移）， 转移地址未知暂时填0。
            # 然后调用语句处理过程处理then语句后面的语句或语句块。 then后的语句处理完后， 当前代码段分配指针的位置就应该是上面的jpc指令的转移位置。
            # 通过前面记录下的jpc指令的位置， 把它的跳转位置改成当前的代码段指针位置。
            #
            # @param fsys FOLLOW集合
            # @param lev 当前层次

    def praseIfStatement(self, fsys, lev):
        self.nextsym()
        nxtlev = set(fsys)
        # FOLLOW(condition)={ then do }
        # 注释：<当型循环语句> ::= while<条件>do<语句>

        nxtlev.add('THEN')
        nxtlev.add('DO')
        self.condition(nxtlev, lev)
        if self.sym.type == 'THEN':
            self.nextsym()
        else:
            self.myErr.report(16, self.sym.lineno)

        cx1 = self.interp.arrayPtr  # 保存当前指令地址
        self.interp.gen(Pcode.Pcode.JPC, 0, 0)  # 生成条件跳转指令，跳转地址位置，暂时写0
        self.statement(fsys, lev)  # 处理then后的statement
        self.interp.pcodeArray[cx1].a = self.interp.arrayPtr  # 经statement处理后，cx为then后语句执行
        # 完的位置，它正是前面未定的跳转地址

        if self.sym.type == 'ELSE':
            self.interp.pcodeArray[cx1].a += 1
            self.nextsym()
            tmpPtr = self.interp.arrayPtr
            self.interp.gen(Pcode.Pcode.JMP, 0, 0)
            self.statement(fsys, lev)
            self.interp.pcodeArray[tmpPtr].a = self.interp.arrayPtr


            # 分析<标识符>
            # <过程调用语句> ::= call<标识符>
            # 从符号表中找到call语句右部的标识符， 获得其所在层次和偏移地址。 然后生成相应的cal指令。 至于调用子过程所需的保护现场等工作
            # 是由类PCODE解释程序在解释执行cal指令时自动完成的
            #
            # @param fsys FOLLOW集合
            # @param lev 当前层次

    def praseCallStatement(self, fsys, lev):
        self.nextsym()
        if self.sym.type == 'ID':  # 检查符号表中该标识符是否已声明
            index = self.table.position(self.sym.value)
            if index != 0:  # 若table中无此名字，返回0
                item = self.table.get(index)
                if item.type == SymbolTable.SymbolTable.Item.procedure:  # 检查该标识符的类型是否为procedure
                    self.interp.gen(Pcode.Pcode.CAL, lev - item.lev, item.addr)
                else:
                    self.myErr.report(15, self.sym.lineno)  # call后标识符应为过程
            else:
                self.myErr.report(11, self.sym.lineno)  # 过程调用未找到
            self.nextsym()
        else:
            self.myErr.report(14, self.sym.lineno)  # all后应为标识符


            # 分析'(' <表达式> { , <表达式> } ')'
            # <写语句> ::= write '(' <表达式> { , <表达式> } ')' 在语法正确的前提下，生成指令： 通过循环调用表达式处理过程
            # 分析write语句括号中的每一个表达式， 生成相应指令 保证把表达式的值算出并放到数据栈顶 并生成14号操作的opr指令， 输出表达式的值。
            # 最后生成15号操作的opr指令，输出一个换行
            #
            # @param fsys FOLLOW集合
            # @param lev 当前层次

    def praseWriteStatement(self, fsys, lev):
        self.nextsym()
        if self.sym.type == 'LPAREN':
            while True:
                self.nextsym()
                nxtlev = set(fsys)
                nxtlev.add('RPAREN')
                nxtlev.add('DOU')
                self.expression(nxtlev, lev)
                self.interp.gen(Pcode.Pcode.OPR, 0, 14)  # OPR 0 14:输出栈顶的值

                if self.sym.type != 'DOU':
                    break
            if self.sym.type == 'RPAREN':  # 解析成功
                self.nextsym()
            else:
                self.myErr.report(33, self.sym.lineno)
        else:
            self.myErr.report(34, self.sym.lineno)
        self.interp.gen(Pcode.Pcode.OPR, 0, 15)  # OPR 0 15:输出换行


        # 分析'(' <标识符> { , <标识符> } ')'
        # <读语句> ::= read '(' <标识符> { , <标识符> } ')' 确定read语句语法合理的前提下（否则报错）， 生成相应的指令：
        # 第一条是16号操作的opr指令， 实现从标准输入设备上读一个整数值，放在数据栈顶。 第二条是sto指令，
        # 把栈顶的值存入read语句括号中的变量所在的单元
        #
        # @param fsys FOLLOW集合
        # @param lev 当前层次

    def praseReadStatement(self, fsys, lev):
        self.nextsym()
        if self.sym.type == 'LPAREN':  # 左括号
            index = 0
            while True:
                self.nextsym()
                if self.sym.type == 'ID':  # 标识符
                    index = self.table.position(self.sym.value)
                if index == 0:
                    self.myErr.report(35, self.sym.lineno)
                else:

                    item = self.table.get(index)
                    if item.type != SymbolTable.SymbolTable.Item.variable:  # 判断符号表中的该符号类型是否为变量
                        self.myErr.report(32, self.sym.lineno)
                    else:
                        self.interp.gen(Pcode.Pcode.OPR, 0, 16)  # OPR 0 16:读入一个数据
                        self.interp.gen(Pcode.Pcode.STO, lev - item.lev, item.addr)  # TO L A;存储变量
                self.nextsym()

                if self.sym.type != 'DOU':
                    break
        else:
            self.myErr.report(34, self.sym.lineno)

        if self.sym.type == 'RPAREN':  # 匹配成功
            self.nextsym()
        else:
            self.myErr.report(33, self.sym.lineno)
            while self.sym.type in fsys is False:
                self.nextsym()

                # 分析:=<表达式>
                # <赋值语句> ::= <标识符>:=<表达式>
                # 首先获取赋值号左边的标识符， 从符号表中找到它的信息， 并确认这个标识符确为变量名。 然后通过调用表达式处理过程 算得赋值号右部的表达式的值
                # 并生成相应的指令 保证这个值放在运行期的数据栈顶。 最后通过前面查到的左部变量的位置信息， 生成相应的sto指令， 把栈顶值存入指定的变量的空间，
                # 实现了赋值操作。
                #
                # @param fsys FOLLOW集合
                # @param lev 当前层次

    def praseAssignStatement(self, fsys, lev):
        # 从符号表中找到该标识符的信息
        index = self.table.position(self.sym.value)
        if index > 0:
            item = self.table.get(index)
            if item.type == SymbolTable.SymbolTable.Item.variable:

                self.nextsym()
                if self.sym.type == 'GIVE':
                    self.nextsym()
                else:
                    self.myErr.report(13, self.sym.lineno)
                nxtlev = set(fsys)

                self.expression(nxtlev, lev)  # 解析表达式
                # expression将执行一系列指令，
                # 但最终结果将会保存在栈顶，
                # 执行sto命令完成赋值
                self.interp.gen(Pcode.Pcode.STO, lev - item.lev, item.addr)
            else:
                self.myErr.report(12, self.sym.lineno)
        else:
            self.myErr.report(11, self.sym.lineno)


            # 分析<表达式>
            # <表达式> ::= [+|-]<项>{<加法运算符><项>} 根据PL/0语法可知，
            # 表达式应该是由正负号或无符号开头、由若干个项以加减号连接而成。 而项是由若干个因子以乘除号连接而成， 因子则可能是一个标识符或一个数字，
            # 或是一个以括号括起来的子表达式。 根据这样的结构，构造出相应的过程， 递归调用就完成了表达式的处理。
            # 把项和因子独立开处理解决了加减号与乘除号的优先级问题。 在这几个过程的反复调用中，始终传递fsys变量的值，
            # 保证可以在出错的情况下跳过出错的符号，使分析过程得以进行下去
            #
            # @param fsys FOLLOW集合
            # @param lev 当前层次

    def expression(self, fsys, lev):
        if self.sym.type == 'PLUS' or self.sym.type == 'MINUS':
            addOperatorType = self.sym.type
            self.nextsym()
            nxtlev = set(fsys)
            nxtlev.add('PLUS')
            nxtlev.add('MINUS')
            self.term(nxtlev, lev)
            if addOperatorType == 'MINUS':  # OPR 0 1:：NEG取反
                self.interp.gen(Pcode.Pcode.OPR, 0, 1)
                # 如果不是负号就是正号，不需生成相应的指令
        else:
            nxtlev = set(fsys)
            nxtlev.add('PLUS')
            nxtlev.add('MINUS')
            self.term(nxtlev, lev)

        # 分析{<加法运算符><项>}
        while self.sym.type == 'PLUS' or self.sym.type == 'MINUS':
            addOperatorType = self.sym.type
            # addOperatorType=word_anay.tokens.index(addOperatorType)
            addOperatorType = FUNC[addOperatorType]
            # print(addOperatorType)
            self.nextsym()
            nxtlev = set(fsys)
            nxtlev.add('PLUS')
            nxtlev.add('MINUS')
            self.term(nxtlev, lev)
            self.interp.gen(Pcode.Pcode.OPR, 0, addOperatorType)

    # 分析<项>
    #  <项> ::= <因子>{<乘法运算符><因子>}
    #
    #  @param fsys FOLLOW集合
    #  @param lev 当前层次
    def term(self, fsys, lev):
        # 分析 < 因子 >
        nxtlev = set(fsys)
        # FOLLOW(factor)={ * /}
        # 一个因子后应当遇到乘号或除号
        nxtlev.add('TIMES')
        nxtlev.add('DIVIDE')
        self.factor(nxtlev, lev)

        # 分析{<乘法运算符><因子>}
        while self.sym.type == 'TIMES' or self.sym.type == 'DIVIDE':
            mulOperatorType = self.sym.type
            # mulOperatorType=word_anay.tokens.index(mulOperatorType)
            mulOperatorType = FUNC[str(mulOperatorType)]
            # print(mulOperatorType)
            self.nextsym()
            self.factor(nxtlev, lev)

            self.interp.gen(Pcode.Pcode.OPR, 0, mulOperatorType)



            # 分析<因子>
            # <因子>=<标识符>|<无符号整数>|'('<表达式>')' 开始因子处理前，先检查当前token是否在facbegsys集合中。
            # 如果不是合法的token，抛24号错误，并通过fsys集恢复使语法处理可以继续进行
            #
            # @param fsys FOLLOW集合
            # @param lev 当前层次

    def factor(self, fsys, lev):
        self.test(self.facbegsys, fsys, 24)  # !!!!!!有问题 // 检测因子的开始符号
        if self.sym.type in self.facbegsys:
            if self.sym.type == 'ID':  # 因子为常量或变量或者过程名
                index = self.table.position(self.sym.value)
                if index > 0:  # 大于0:找到，等于0:未找到
                    item = self.table.get(index)
                    if item.type == SymbolTable.SymbolTable.Item.constant:  # 如果这个标识符对应的是常量，值为val，生成lit指令，把val放到栈顶
                        self.interp.gen(Pcode.Pcode.LIT, 0, item.value)  # 生成lit指令，把这个数值字面常量放到栈顶
                    elif item.type == SymbolTable.SymbolTable.Item.variable:
                        # 把位于距离当前层level的层的偏移地址为adr的变量放到栈顶
                        self.interp.gen(Pcode.Pcode.LOD, lev - item.lev, item.addr)
                    elif item.type == SymbolTable.SymbolTable.Item.procedure:
                        self.myErr.report(21, self.sym.lineno)  # 表达式内不可有过程标识符
                else:
                    self.myErr.report(11, self.sym.lineno)  # 标识符未声明
                self.nextsym()
            elif self.sym.type == 'NUMBER':  # 因子为数
                num = self.sym.value
                if num > SymbolTable.SymbolTable.addrMax:  # 数越界
                    self.myErr.report(31, self.sym.lineno)
                    num = 0
                self.interp.gen(Pcode.Pcode.LIT, 0, num)  # 生成lit指令，把这个数值字面常量放到栈顶
                self.nextsym()
            elif self.sym.type == 'LPAREN':  # 因子为表达式：'('<表达式>')'
                self.nextsym()
                nxtlev = set(fsys)
                # FOLLOW(expression) = { )}
                nxtlev.add('RPAREN')
                self.expression(nxtlev, lev)
                if self.sym.type == 'RPAREN':  # 匹配成功
                    self.nextsym()
                else:
                    self.myErr.report(22, self.sym.lineno)  # 缺少右括号
            else:  # 做补救措施
                self.test(fsys, self.facbegsys, 23)  # 一个因子处理完毕，遇到的token应在fsys集合中
                # 如果不是，抛23号错，并找到下一个因子的开始，使语法分析可以继续运行下去


                # 分析<条件>
                # <表达式><关系运算符><表达式>|odd<表达式>
                # 首先判断是否为一元逻辑表达式：判奇偶。 如果是，则通过调用表达式处理过程分析计算表达式的值， 然后生成判奇指令。
                # 如果不是，则肯定是二元逻辑运算符， 通过调用表达式处理过程依次分析运算符左右两部分的值， 放在栈顶的两个空间中，然后依不同的逻辑运算符，
                # 生成相应的逻辑判断指令，放入代码段。
                #
                # @param fsys FOLLOW集合
                # @param lev 当前层次

    def condition(self, fsys, lev):
        if self.sym.type == 'ODD':
            self.nextsym()
            self.expression(fsys, lev)
            self.interp.gen(Pcode.Pcode.OPR, 0, 6)  # OPR 0 6:判断栈顶元素是否为奇数
        else:
            nxtlev = set(fsys)
            # FOLLOW(expression)={  =  !=  <  <=  >  >= }
            nxtlev.add('EQUAL')
            nxtlev.add('UNEQUAL')
            nxtlev.add('LESS')
            nxtlev.add('LORE')
            nxtlev.add('MORE')
            nxtlev.add('MOE')
            self.expression(nxtlev, lev)

            if self.sym.type == 'EQUAL' or self.sym.type == 'UNEQUAL' or self.sym.type == 'LESS' or self.sym.type == "LORE" or self.sym.type == 'MORE' or self.sym.type == 'MOE':
                relationOperatorType = self.sym.type
                # relationOperatorType=word_anay.tokens.index(relationOperatorType)
                relationOperatorType = FUNC[str(relationOperatorType)]
                # print(relationOperatorType)
                self.nextsym()
                self.expression(fsys, lev)
                self.interp.gen(Pcode.Pcode.OPR, 0, relationOperatorType)
            else:
                self.myErr.report(20, self.sym.lineno)

    @staticmethod
    def debug(msg):
        print("*** DEDUG : " + str(msg) + "  ***")
