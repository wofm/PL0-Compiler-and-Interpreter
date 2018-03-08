import time

import Pcode


class Interpreter:
    stackSize = 1000  # 运行栈上限
    arraySize = 500  # pcode数组上限
    listswitch = True  # 显示虚拟代码与否

    def __init__(self,out_file):
        self.arrayPtr = 0
        self.pcodeArray = list()
        self.out_file=out_file
        for i in range(Interpreter.arraySize):  # 初始化
            self.pcodeArray.append(Pcode.Pcode(0, 0, 0))

    # 生成虚拟机代码
    def gen(self, f, l, a):
        if self.arrayPtr >= Interpreter.arraySize:
            raise Exception("***ERROR:Program too long***")
        self.pcodeArray[self.arrayPtr] = Pcode.Pcode(f, l, a)
        self.arrayPtr += 1

    # 输出目标代码清单 start:开始输出的位置
    def listcode(self, start):
        if Interpreter.listswitch == True:
            for i in range(start, self.arrayPtr):
                try:
                    msg=str(i) + " " + str(Pcode.Pcode.pcode[self.pcodeArray[i].f]) + " " + str(self.pcodeArray[i].l) + " " +str(self.pcodeArray[i].a)
                    # print(msg)
                    self.out_file.write(msg)
                    self.out_file.write('\n')

                except Exception:
                    print("***list pcode meet with error***")

    # 通过给定的层次差来获得该层的堆栈帧基址
    # l 目标层次与当前层次的层次差
    # runtimeStack 运行栈
    # b 当前层堆栈帧基地址
    # return 目标层次的堆栈帧基地址
    def base(self, l, runtimeStack, b):
        while l > 0:
            b = runtimeStack[b]
            l -= 1
        return b

    # 这个过程模拟了一台可以运行类PCODE指令的栈式计算机。 它拥有一个栈式数据段用于存放运行期数据, 拥有一个代码段用于存放类PCODE程序代码。
    # 同时还拥用数据段分配指针、指令指针、指令寄存器、局部段基址指针等寄存器。
    # stdin  从键盘输入无符号整数
    # stdout  显示pcode运行过程
    # todo 参数设置
    def interpret(self, stdin, stdout,signal):
        runtimeStack = list()
        for i in range(Interpreter.arraySize):  # 初始化
            runtimeStack.append(0)
        #print("***Start Interpret P_CODE***")
        pc = 0  # 指令指针
        bp = 0  # 指令基址
        sp = 0 #sp:栈顶指针
        while True:
            index = self.pcodeArray[pc]  # index :存放当前指令, 读当前指令
            pc += 1
            #print(str(pc) + " " + str(Pcode.Pcode.pcode[index.f]) + " " + str(index.l) + " " + str(index.a))
            if index.f == Pcode.Pcode.LIT:
                runtimeStack[sp] = index.a
                sp += 1
            elif index.f == Pcode.Pcode.OPR:
                if index.a == 0:#ok 每个过程出口都要使用的释放数据段指令
                    sp = bp
                    pc = runtimeStack[sp + 2]
                    bp = runtimeStack[sp + 1]
                elif index.a == 1:#ok 取反
                    runtimeStack[sp - 1] = -runtimeStack[sp - 1]
                elif index.a == 2:# + PLUS
                    sp -= 1
                    runtimeStack[sp - 1] += runtimeStack[sp]
                elif index.a == 3:#- MINUS
                    sp -= 1
                    runtimeStack[sp - 1] -= runtimeStack[sp]
                elif index.a == 4:# * TIMES
                    sp -= 1
                    runtimeStack[sp - 1] = runtimeStack[sp - 1] * runtimeStack[sp]
                elif index.a == 5:# / DIVIDE
                    sp -= 1
                    runtimeStack[sp - 1] //= runtimeStack[sp]  # TODO 除号问题
                elif index.a == 6:#ok
                    runtimeStack[sp - 1] %= 2
                elif index.a == 7:#number
                    sp -= 1
                    runtimeStack[sp - 1] %= runtimeStack[sp]
                elif index.a == 8:# = EQUAL
                    sp -= 1
                    if runtimeStack[sp] == runtimeStack[sp - 1]:
                        runtimeStack[sp - 1] = 1
                    else:
                        runtimeStack[sp - 1] = 0
                elif index.a == 9:#UNEQUAL
                    sp -= 1
                    if runtimeStack[sp] != runtimeStack[sp - 1]:
                        runtimeStack[sp - 1] = 1
                    else:
                        runtimeStack[sp - 1] = 0
                elif index.a == 10:#< less
                    sp -= 1
                    if runtimeStack[sp-1] < runtimeStack[sp]:
                        runtimeStack[sp - 1] = 1
                    else:
                        runtimeStack[sp - 1] = 0
                elif index.a == 11:#>= GORE
                    sp -= 1
                    if runtimeStack[sp-1] >= runtimeStack[sp]:
                        runtimeStack[sp - 1] = 1
                    else:
                        runtimeStack[sp - 1] = 0
                elif index.a == 12:#> MORE
                    sp -= 1
                    if runtimeStack[sp-1] > runtimeStack[sp]:
                        runtimeStack[sp - 1] = 1
                    else:
                        runtimeStack[sp - 1] = 0
                elif index.a == 13:#<= LORE
                    sp -= 1
                    if runtimeStack[sp-1] <= runtimeStack[sp]:
                        runtimeStack[sp - 1] = 1
                    else:
                        runtimeStack[sp - 1] = 0
                elif index.a == 14:# ok 输出栈顶的值
                    #print("runtimeStack[sp - 1]" +"   "+  str(runtimeStack[sp - 1]) + ' ')
                    try:
                        stdout.write(" " + str(runtimeStack[sp - 1]) + ' ')
                        stdout.flush()
                    except Exception:
                        print("***case 14 meet with error***")
                    sp -= 1
                elif index.a == 15:#ok 输出换行
                    #print()
                    try:
                        stdout.write("\n")
                    except Exception:
                        print("***case 15 meet with error***")
                elif index.a == 16:#ok,读入数据
                    #print("Please Input a Integer : ")
                    stdin.append('Please Input a Integer : ')
                    runtimeStack[sp] = 0
                    # TODO change
                    try:
                        #t=input()
                        while True:
                            check=stdin.toPlainText()
                            data=stdin.toPlainText().split()
                           # print(data)
                            if data[-1]!=':' and check[-1]=='\n':
                                #print("t=" + data[-1])
                                t=int(data[-1])

                                break
                            time.sleep(0.1)

                        runtimeStack[sp] = int(t)
                        #print(str(runtimeStack[sp]))
                        sp += 1
                    except Exception as e:
                        print(e)
                        #print("***read data meet with error***")
                    # try:
                    #     stdout.write(" " + str(runtimeStack[sp]) + '\n')
                    #     stdout.flush()
                    # except Exception:
                    #     print("***case 16 meet with error***")
            elif index.f == Pcode.Pcode.LOD:
                runtimeStack[sp] = runtimeStack[self.base(index.l, runtimeStack, bp) + index.a]
                sp += 1
            elif index.f == Pcode.Pcode.STO:
                sp -= 1
                runtimeStack[self.base(index.l, runtimeStack, bp) + index.a] = runtimeStack[sp]
            elif index.f == Pcode.Pcode.CAL:
                runtimeStack[sp] = self.base(index.l, runtimeStack, bp)  # 将静态作用域基地址入栈
                runtimeStack[sp + 1] = bp  # 将动态作用域基地址
                runtimeStack[sp + 2] = pc  # 将当前指针入栈
                bp = sp  # 改变基地址指针值为新过程的基地址
                pc = index.a
            elif index.f == Pcode.Pcode.INT:
                sp += index.a
            elif index.f == Pcode.Pcode.JMP:
                pc = index.a
            elif index.f == Pcode.Pcode.JPC:
                sp -= 1
                if runtimeStack[sp] == 0:
                    pc = index.a

            if pc == 0:
                signal[0]='b'
                stdout.close()
                break

    def debugPcodeArray(self):
        #print("***Auto-Generated Pcode Array***")
        i = 0
        while (i < self.arrayPtr):
            #print("" + str(i) + "  " + str(Pcode.Pcode.pcode[self.pcodeArray[i].f]) + "  " + str(self.pcodeArray[i].l) + "  " +str(self.pcodeArray[i].a))
            i+=1
            # TODO PL0writer
