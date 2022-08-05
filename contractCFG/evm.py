from os import dup
from z3 import *
from util import *
from varGenerator import Generator

class EVM:
    def __init__(self, stack, pc):
        self.stack = stack
        self.pc = pc
        self.code_size = 0
        self.solver = Solver()
        self.generator = Generator()
        self.address = BitVec('address', 256)
        self.caller = BitVec('caller', 256)
        self.origin = BitVec('origin', 256)
        self.value = BitVec('value', 256)
        self.gas_price = BitVec('gasPrice', 256)
        self.coinbase = BitVec('coninbase', 256)
        self.timestamp = BitVec('timestamp', 256)
        self.block_number = BitVec('block_number', 256)
        self.difficulty = BitVec('difficulty', 256)
        self.gas_limit = BitVec('gas_limit', 256)
        self.balance = BitVec('self_balance', 256)
        self.basefee = BitVec('basefee', 256)
        self.target = -1

    def setPc(self, pc):
        self.pc = pc

    def setCodeSize(self, code_size):
        self.code_size = code_size
    
    def STOP(self): #00
        self.pc = self.pc + 1
        return

    def ADD(self): #01
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            if isReal(first) and isSymbolic(second):
                first = BitVecVal(first, 256)
            elif isSymbolic(first) and isReal(second):
                second = BitVecVal(second, 256)
            computed = (first + second) & (2 ** 256 - 1) #截断，最大256位
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError("STACK underflow")

    def MUL(self): #02
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            if isReal(first) and isSymbolic(second):
                first = BitVecVal(first, 256)
            elif isSymbolic(first) and isReal(second):
                second = BitVecVal(second, 256)
            computed = (first * second) & (2 ** 256 - 1) #截断，最大256位
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError("STACK underflow")

    def SUB(self): #03
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            if isReal(first) and isSymbolic(second):
                first = BitVecVal(first, 256)
            elif isSymbolic(first) and isReal(second):
                second = BitVecVal(second, 256)
            computed = (first - second) & (2 ** 256 - 1) #截断，最大256位
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError("STACK underflow")

    def DIV(self): #04
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            if isReal(first) and isReal(second):
                if second == 0:
                    computed = 0
                else:
                    first = to_unsigned(first)
                    second = to_unsigned(second)
                    computed = first // second
            else:
                # first = to_symbolic(first)
                # second = to_symbolic(second)
                # self.solver.push()
                # self.solver.add( Not(second == 0))
                # if check_sat(self.solver) == unsat:
                #     computed = 0
                # else:
                #     computed = UDiv(first, second)
                # self.solver.pop()
                computed = BitVec(self.generator.gen_stack_var(), 256)
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError("STACK underflow")

    def SDIV(self): #05
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            if isReal(first) and isReal(second):
                first = to_signed(first)
                second = to_signed(second)
                if second == 0:
                    computed = 0
                elif first == -2 ** 255 and second == -1:
                    computed = -2 * 255
                else:
                    sign = -1 if (first // second) < 0 else 1
                    computed = sign * (abs(first) // abs(second))
            else:
                # first = to_symbolic(first)
                # second = to_symbolic(second)
                # self.solver.push()
                # self.solver.add( Not(second == 0))
                # if check_sat(self.solver) == unsat:
                #     computed = 0
                # else:
                #     self.solver.push()
                #     self.solver.add(Not(And(first == -2 ** 255, second == -1)))
                #     if check_sat(self.solver) == unsat:
                #         computed = -2 ** 255
                #     else:
                #         self.solver.push()
                #         self.solver.add(first / second < 0)
                #         sign = -1 if check_sat(self.solver) == sat else 1
                #         z3_abs = lambda x: If(x >= 0, x, -x)
                #         first = z3_abs(first)
                #         second = z3_abs(second)
                #         computed = sign * (first / second)
                #         self.solver.pop()
                #     self.solver.pop()
                # self.solver.pop()
                computed = BitVec(self.generator.gen_stack_var(), 256)
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError("STACK underflow")

    def MOD(self): #06
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            if isReal(first) and isReal(second):
                if second == 0:
                    computed = 0
                else:
                    first = to_unsigned(first)
                    second = to_unsigned(second)
                    computed = first % second & (2 ** 256 - 1) #截断
            else:
                # first = to_symbolic(first)
                # second = to_symbolic(second)
                # self.solver.push()
                # self.solver.add( Not(second == 0))
                # if check_sat(self.solver) == unsat:
                #     computed = 0
                # else:
                #     computed = URem(first, second)
                # self.solver.pop()
                computed = BitVec(self.generator.gen_stack_var(), 256)
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError("STACK underflow")

    def SMOD(self): #07
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            if isReal(first) and isReal(second):
                if second == 0:
                    computed = 0
                else:
                    first = to_signed(first)
                    second = to_signed(second)
                    sign = -1 if first < 0 else 1
                    computed = sign * (abs(first) % abs(second))
            else:
                # first = to_symbolic(first)
                # second = to_symbolic(second)
                # self.solver.push()
                # self.solver.add( Not(second == 0))
                # if check_sat(self.solver) == unsat:
                #     computed = 0
                # else:
                #     self.solver.push()
                #     self.solver.add(first < 0)
                #     sign = BitVecVal(-1, 256) if check_sat(self.solver) == sat else BitVecVal(1, 256)
                #     self.solver.pop()
                #     z3_abs = lambda x: If(x >= 0, x, -x)
                #     first = z3_abs(first)
                #     second = z3_abs(second)
                #     computed = sign * (first % second)
                # self.solver.pop()
                computed = BitVec(self.generator.gen_stack_var(), 256)
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError("STACK underflow")
    
    def ADDMOD(self): #08
        if len(self.stack) > 2:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            third = self.stack.pop(0)

            if isAllReal(first, second, third):
                if third == 0:
                    computed = 0
                else:
                    computed = (first + second) % third
            else:
                # first = to_symbolic(first)
                # second = to_symbolic(second)
                # self.solver.push()
                # self.solver.add( Not(third == 0) )
                # if check_sat(self.solver) == unsat:
                #     computed = 0
                # else:
                #     first = ZeroExt(256, first)
                #     second = ZeroExt(256, second)
                #     third = ZeroExt(256, third)
                #     computed = (first + second) % third
                #     computed = Extract(255, 0, computed)
                # self.solver.pop()
                computed = BitVec(self.generator.gen_stack_var(), 256)
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def MULMOD(self): #09
        if len(self.stack) > 2:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            third = self.stack.pop(0)

            if isAllReal(first, second, third):
                if third == 0:
                    computed = 0
                else:
                    computed = (first * second) % third
            else:
                # first = to_symbolic(first)
                # second = to_symbolic(second)
                # self.solver.push()
                # self.solver.add( Not(third == 0) )
                # if check_sat(self.solver) == unsat:
                #     computed = 0
                # else:
                #     first = ZeroExt(256, first)
                #     second = ZeroExt(256, second)
                #     third = ZeroExt(256, third)
                #     computed = URem(first * second, third)
                #     computed = Extract(255, 0, computed)
                # self.solver.pop()
                computed = BitVec(self.generator.gen_stack_var(), 256)
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def EXP(self): #0A z3不能实现幂运算
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            base = self.stack.pop(0)
            exponent = self.stack.pop(0)
            # Type conversion is needed when they are mismatched
            if isAllReal(base, exponent):
                computed = pow(base, exponent, 2**256)
            else:
                # The computed value is unknown, this is because power is
                # not supported in bit-vector theory
                new_var_name = self.generator.gen_arbitrary_var()
                computed = BitVec(new_var_name, 256)
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def SIGNEXTEND(self): #0B
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            if isAllReal(first, second):
                if first >= 32 or first < 0:
                    computed = second
                else:
                    signbit_index_from_right = 8 * first + 7
                    if second & (1 << signbit_index_from_right):
                        computed = second | (2 ** 256 - (1 << signbit_index_from_right))
                    else:
                        computed = second & ((1 << signbit_index_from_right) - 1 )
            else:
                # first = to_symbolic(first)
                # second = to_symbolic(second)
                # self.solver.push()
                # self.solver.add( Not( Or(first >= 32, first < 0 ) ) )
                # if check_sat(self.solver) == unsat:
                #     computed = second
                # else:
                #     signbit_index_from_right = 8 * first + 7
                #     self.solver.push()
                #     self.solver.add(second & (1 << signbit_index_from_right) == 0)
                #     if check_sat(self.solver) == unsat:
                #         computed = second | (2 ** 256 - (1 << signbit_index_from_right))
                #     else:
                #         computed = second & ((1 << signbit_index_from_right) - 1)
                #     self.solver.pop()
                # self.solver.pop()
                computed = BitVec(self.generator.gen_stack_var(), 256)
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def LT(self): #10
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            if isAllReal(first, second):
                first = to_unsigned(first)
                second = to_unsigned(second)
                if first < second:
                    computed = 1
                else:
                    computed = 0
            else:
                computed = If(ULT(first, second), BitVecVal(1, 256), BitVecVal(0, 256))
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def GT(self): #11
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            if isAllReal(first, second):
                first = to_unsigned(first)
                second = to_unsigned(second)
                if first > second:
                    computed = 1
                else:
                    computed = 0
            else:
                computed = If(UGT(first, second), BitVecVal(1, 256), BitVecVal(0, 256))
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def SLT(self): #12 可能需要改进?
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            if isAllReal(first, second):
                first = to_signed(first)
                second = to_signed(second)
                if first < second:
                    computed = 1
                else:
                    computed = 0
            else:
                computed = If(first < second, BitVecVal(1, 256), BitVecVal(0, 256))
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def SGT(self): #13 可能需要改进?
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            if isAllReal(first, second):
                first = to_signed(first)
                second = to_signed(second)
                if first > second:
                    computed = 1
                else:
                    computed = 0
            else:
                computed = If(first > second, BitVecVal(1, 256), BitVecVal(0, 256))
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def EQ(self): #14
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            if isAllReal(first, second):
                if first == second:
                    computed = 1
                else:
                    computed = 0
            else:
                computed = If(first == second, BitVecVal(1, 256), BitVecVal(0, 256))
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def ISZERO(self): #15
        # Tricky: this instruction works on both boolean and integer,
        # when we have a symbolic expression, type error might occur
        # Currently handled by try and catch
        if len(self.stack) > 0:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            if isReal(first):
                if first == 0:
                    computed = 1
                else:
                    computed = 0
            else:
                computed = If(first == 0, BitVecVal(1, 256), BitVecVal(0, 256))
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def AND(self): #16
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            computed = first & second
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def OR(self): #17
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            computed = first | second
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def XOR(self): #18
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            second = self.stack.pop(0)
            computed = first ^ second
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def NOT(self): #19
        if len(self.stack) > 0:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            computed = (~first) & (2 ** 256 - 1)
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def BYTE(self): #1A
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            first = self.stack.pop(0)
            byte_index = 32 - first - 1
            second = self.stack.pop(0)

            if isAllReal(first, second):
                if first >= 32 or first < 0:
                    computed = 0
                else:
                    computed = second & (255 << (8 * byte_index))
                    computed = computed >> (8 * byte_index)
            else:
                # first = to_symbolic(first)
                # second = to_symbolic(second)
                # self.solver.push()
                # self.solver.add( Not (Or( first >= 32, first < 0 ) ) )
                # if check_sat(self.solver) == unsat:
                #     computed = 0
                # else:
                #     computed = second & (255 << (8 * byte_index))
                #     computed = computed >> (8 * byte_index)
                # self.solver.pop()
                computed = BitVec(self.generator.gen_stack_var(), 256)
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def SHL(self): #1B 需检查
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            shift = self.stack.pop(0)
            value = self.stack.pop(0)

            if isAllReal(shift, value):
                if shift >=0 and shift < 256:
                    computed = (value << shift) % (2 ** 256)
                else:
                    computed = 0
            else:
                # shift = to_symbolic(shift)
                # value = to_symbolic(value)
                # self.solver.push()
                # self.solver.add(And(shift >= 0, shift < 256))
                # if check_sat(self.solver) == unsat:
                #     computed = 0
                # else:
                #     computed = (value << shift) % (2 ** 256)
                # self.solver.pop()
                computed = BitVec(self.generator.gen_stack_var(), 256)
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def SHR(self): #1C
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            shift = self.stack.pop(0)
            value = self.stack.pop(0)

            if isAllReal(shift, value):
                if shift >=0 and shift < 256:
                    computed = value >> shift
                else:
                    computed = 0
            else:
                # shift = to_symbolic(shift)
                # value = to_symbolic(value)
                # self.solver.push()
                # self.solver.add(And(shift >= 0, shift < 256))
                # if check_sat(self.solver) == unsat:
                #     computed = 0
                # else:
                #     computed = value >> shift
                # self.solver.pop()
                computed = BitVec(self.generator.gen_stack_var(), 256)
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def SAR(self): #1D
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            shift = self.stack.pop(0)
            value = self.stack.pop(0)

            if isAllReal(shift, value):
                value = to_signed(value)
                if value >= 0:
                    computed = BitVecVal(value / (2 ** shift), 256)
                else:
                    if abs(value) < 2 ** shift:
                        computed = BitVecVal(-1, 256)
                    else:
                        computed = BitVecVal(abs(value) / (2 ** shift) * (-1), 256)
            else:
                # shift = to_symbolic(shift)
                # value = to_symbolic(value)
                # self.solver.push()
                # self.solver.add(value >= 0)
                # if check_sat(self.solver) == unsat:
                #     self.solver.push()
                #     self.solver.add(abs(value) >= 2 ** shift)
                #     if check_sat(self.solver) == unsat:
                #         computed = BitVecVal(-1, 256)
                #     else:
                #         computed = abs(value) / (2 ** shift) * (-1)
                #     self.solver.pop()
                # else:
                #     computed = value / (2 ** shift)
                # self.solver.pop()
                computed = BitVec(self.generator.gen_stack_var(), 256)
            computed = simplify(computed) if is_expr(computed) else computed
            self.stack.insert(0, computed)
            # self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')

    def SHA3(self): #20
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
        else:
            raise ValueError('STACK underflow')


    def ADDRESS(self): #30
        self.pc = self.pc + 1
        self.stack.insert(0, self.address)

    def BALANCE(self): #31
        if len(self.stack) > 0:
            self.pc = self.pc + 1
            address = self.stack.pop(0)
            balance = BitVec(str(address) + "_balance", 256)
            self.stack.insert(0, balance)

    def ORIGIN(self): #32
        self.pc = self.pc + 1
        self.stack.insert(0, self.origin)

    def CALLER(self): #33
        self.pc = self.pc + 1
        self.stack.insert(0, self.caller)

    def CALLVALUE(self): #34
        self.pc = self.pc + 1
        self.stack.insert(0, self.value)

    def CALLDATALOAD(self): #35
        if len(self.stack) > 0:
            self.pc =self.pc + 1
            position = self.stack.pop(0)
            self.stack.insert(0, BitVec(self.generator.gen_data_var(position), 256))
        else:
            raise ValueError('STACK underflow')

    def CALLDATASIZE(self): #36
        self.pc = self.pc + 1
        self.stack.insert(0, BitVec(self.generator.gen_data_size(), 256))

    def CALLDATACOPY(self): #37
        if len(self.stack) > 2:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
        else:
            raise ValueError('STACK underflow')

    def CODESIZE(self): #38
        self.pc =self.pc + 1
        self.stack.insert(0, self.code_size)

    def CODECOPY(self): #39
        if len(self.stack) > 2:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
        else:
            raise ValueError('STACK underflow')

    def GASPRICE(self): #3A
        self.pc =self.pc + 1
        self.stack.insert(0, self.gas_price)

    def EXTCODESIZE(self): #3B
        if len(self.stack) > 0:
            self.pc =self.pc + 1
            address = self.stack.pop(0)
            self.stack.insert(0, BitVec(self.generator.gen_code_size_var(address), 256))
        else:
            raise ValueError('STACK underflow')

    def EXTCODECOPY(self): #3C
        if len(self.stack) > 3:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
        else:
            raise ValueError('STACK underflow')

    def RETURNDATASIZE(self): #3D
        self.pc =self.pc + 1
        self.stack.insert(0, BitVec(self.generator.gen_arbitrary_var(), 256))

    def RETURNDATACOPY(self): #3E
        if len(self.stack) > 2:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
        else:
            raise ValueError('STACK underflow')

    def EXTCODEHASH(self): #3F
        if len(self.stack) > 0:
            self.pc = self.pc + 1
            address = self.stack.pop(0)
            code_hash = BitVec(str(address) + "_hash", 256)
            self.stack.insert(0, code_hash)
        else:
            raise ValueError('STACK underflow')

    def BLOCKHASH(self): #40
        if len(self.stack) > 0:
            self.pc = self.pc + 1
            blocknumber = self.stack.pop(0)
            self.stack.insert(0, BitVec('block_hash_' + str(blocknumber), 256))
        else:
            raise ValueError('STACK underflow')

    def COINBASE(self): #41
        self.pc = self.pc + 1
        self.stack.insert(0, self.coinbase)

    def TIMESTAMP(self): #42
        self.pc = self.pc + 1
        self.stack.insert(0, self.timestamp)

    def NUMBER(self): #43
        self.pc = self.pc + 1
        self.stack.insert(0, self.block_number)

    def DIFFICULTY(self): #44
        self.pc = self.pc + 1
        self.stack.insert(0, self.difficulty)

    def GASLIMIT(self): #45
        self.pc = self.pc + 1
        self.stack.insert(0, self.gas_limit)

    def CHAINID(self): #46
        self.pc = self.pc + 1
        self.stack.insert(0, 1)

    def SELFBALANCE(self): #47
        self.pc = self.pc + 1
        self.stack.insert(0, self.balance)

    def BASEFEE(self): #48
        self.pc = self.pc + 1
        self.stack.insert(0, self.basefee)

    def POP(self): #50
        if len(self.stack) > 0:
            self.pc = self.pc + 1
            self.stack.pop(0)
        else:
            raise ValueError('STACK underflow')

    def MLOAD(self): #51
        if len(self.stack) > 0:
            self.pc = self.pc + 1
            offset = self.stack.pop(0)
            value = self.generator.gen_mem_var(offset)
            self.stack.insert(0, BitVec(value, 256))
        else:
            raise ValueError('STACK underflow')

    def MSTORE(self): #52
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
        else:
            raise ValueError('STACK underflow')

    def MSTORE8(self): #53
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
        else:
            raise ValueError('STACK underflow')

    def SLOAD(self): #54
        if len(self.stack) > 0:
            self.pc = self.pc + 1
            key = self.stack.pop(0)
            value = self.generator.gen_owner_store_var(key)
            self.stack.insert(0, BitVec(value, 256))
        else:
            raise ValueError('STACK underflow')

    def SSTORE(self): #55
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
        else:
            raise ValueError('STACK underflow')

    def JUMP(self): #56
        if len(self.stack) > 0:
            target_address = self.stack.pop(0)
            if isSymbolic(target_address):
                try:
                    target_address = int(str(simplify(target_address)))
                except:
                    # raise TypeError("Target address must be an integer")
                    target_address = None
            return target_address
        else:
            raise ValueError('STACK underflow')

    def JUMPI(self): #57
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            target_address = self.stack.pop(0)
            flag = self.stack.pop(0) # 可能为实数0或1，说明跳转与输入无关
            if isSymbolic(target_address):
                try:
                    target_address = int(str(simplify(target_address)))
                except:
                    raise TypeError("Target address must be an integer")
            return target_address, flag
        else:
            raise ValueError('STACK underflow')

    def PC(self): #58
        self.stack.insert(0, self.pc)
        self.pc = self.pc + 1

    def MSIZE(self): #59
        self.pc = self.pc + 1
        self.stack.insert(0, BitVec('msize', 256))

    def GAS(self): #5A
        self.pc = self.pc + 1
        self.stack.insert(0, BitVec(self.generator.gen_gas_var(), 256))

    def JUMPDEST(self): #5B
        self.pc = self.pc + 1

    def PUSH(self, position, value): #60-7F
        self.pc = self.pc + position + 1
        self.stack.insert(0, int(value, 16))

    def DUP(self, index): #80-8F
        position = index - 1
        if len(self.stack) > position:
            self.pc = self.pc + 1
            duplicate = self.stack[position]
            self.stack.insert(0, duplicate)
        else:
            raise ValueError('STACK underflow')

    def SWAP(self, index): #90-9F
        if len(self.stack) > index:
            self.pc = self.pc + 1
            temp = self.stack[index]
            self.stack[index] = self.stack[0]
            self.stack[0] = temp
        else:
            raise ValueError('STACK underflow')

    def LOG(self, number): #A0-A4
        number += 2
        if len(self.stack) > number - 1:
            self.pc = self.pc + 1
            while number > 0:
                self.stack.pop(0)
                number -= 1
        else:
            raise ValueError('STACK underflow')

    def CREATE(self): #F0
        if len(self.stack) > 2:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            new_var_name = self.generator.gen_arbitrary_var()
            new_var = BitVec(new_var_name, 256)
            self.stack.insert(0, new_var)
        else:
            raise ValueError('STACK underflow')

    def CALL(self): #F1
        if len(self.stack) > 6:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
            # self.stack.insert(0, 1)
        else:
            raise ValueError('STACK underflow')

    def CALLCODE(self): #F2
        if len(self.stack) > 6:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
            # self.stack.insert(0, 1)
        else:
            raise ValueError('STACK underflow')

    def RETURN(self): #F3
        if len(self.stack) > 1:
            # self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
        else:
            raise ValueError('STACK underflow')

    def DELEGATECALL(self): #F4
        if len(self.stack) > 5:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
            # self.stack.insert(0, 1)
        else:
            raise ValueError('STACK underflow')

    def CREATE2(self): #F5
        if len(self.stack) > 3:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            new_var_name = self.generator.gen_arbitrary_var()
            new_var = BitVec(new_var_name, 256)
            self.stack.insert(0, new_var)
        else:
            raise ValueError('STACK underflow')

    def STATICCALL(self): #FA
        if len(self.stack) > 5:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.pop(0)
            self.stack.insert(0, BitVec(self.generator.gen_stack_var(), 256))
            # self.stack.insert(0, 1)
        else:
            raise ValueError('STACK underflow')

    def REVERT(self): #FD
        if len(self.stack) > 1:
            self.pc = self.pc + 1
            self.stack.pop(0)
            self.stack.pop(0)
        else:
            raise ValueError('STACK underflow')

    def INVALID(self): #FE
        return

    def SELFDESTRUCT(self): #FF
        if len(self.stack) > 0:
            self.pc = self.pc + 1
            self.stack.pop(0)
        else:
            raise ValueError('STACK underflow')