from basicBlock import *
import logging
import re
import os
import subprocess
from z3 import *
import six
import graphviz

def filteBlocks(basicBlocks):
    keys = list(basicBlocks.keys())
    index = len(keys) - 1
    filte_index = len(keys)
    while(index > 0):
        current_block = basicBlocks[keys[index]]
        pre_block = basicBlocks[keys[index - 1]]
        current_instructions = current_block.getInstructions()
        pre_instructions = pre_block.getInstructions()
        if list(current_instructions.values())[0] != "JUMPDEST" and list(pre_instructions.values())[-1] != "JUMPI":
            filte_index = index
        index -= 1
    while(filte_index < len(keys)):
        basicBlocks.pop(keys[filte_index])
        filte_index += 1

def outputBlocks(basicBlocks, filePath):
    for block in basicBlocks.values():
        instructions = block.getInstructions()
        item = ''
        instrs = list(instructions.values())
        for i in range(0, len(instrs) - 1):
            item = item + instrs[i].split(' ')[0] + ' '
        item = item + instrs[-1].split(' ')[0] + '\n'
        with open(filePath, 'a') as f:
            f.write(item)

def generateGraph(basicBlocks, function_cfg, function_sig):
    dot = graphviz.Digraph(comment=function_sig)
    dot.attr('node', shape='box')
    for key in list(function_cfg.keys()):
        block = basicBlocks[key]
        instructions = block.getInstructions()
        node_text = '<'
        for pc, instr in instructions.items():
            node_text = node_text + str(pc) + ': ' + instr + '<BR ALIGN="LEFT"/>'
        node_text = node_text + '>'
        dot.node(str(key), node_text)
    for key, item in function_cfg.items():
        for next in item["next"]:
            dot.edge(str(key), str(next))
    dot.render("./cfg_graph/" + function_sig +".gv")

def filteCfg(function_cfg, number):
    for key in list(function_cfg.keys()):
        if key == number:
            continue
        if function_cfg[key]["pre"] == [] and function_cfg[key]["next"] == []:
            function_cfg.pop(key)

def instrFormat(instructions):
    for key in list(instructions.keys()):
        # instructions[key].replace("KECCAK256", "SHA3")
        if instructions[key] == "KECCAK256":
            instructions[key] = "SHA3"

def isSymbolic(value):
    return not isinstance(value, six.integer_types)

def isReal(value):
    return isinstance(value, six.integer_types)

def isAllReal(*args):
    for element in args:
        if isSymbolic(element):
            return False
    return True

def to_symbolic(number):
    if isReal(number):
        return BitVecVal(number, 256)
    return number

def to_unsigned(number):
    if number < 0:
        return number + 2**256
    return number

def to_signed(number):
    if number > 2**(256 - 1):
        return (2**(256) - number) * (-1)
    else:
        return number

def check_sat(solver, pop_if_exception=True):
    try:
        ret = solver.check()
        if ret == unknown:
            raise Z3Exception(solver.reason_unknown())
    except Exception as e:
        if pop_if_exception:
            solver.pop()
        raise e
    return ret

def readRuntimeCode(bytecode):
    pattern1 = re.compile("(a165627a7a72305820\\S{64}0029$)|(a265627a7a72315820\\S{64}64736f6c6343\\S{6}0032$)|(a264697066735822\\S{68}64736f6c6343\\S{6}0033$)")
    bytecode = re.sub(pattern1, "", bytecode)
    pattern2 = re.compile("(f300|f3fe)60(80|60)6040")
    group = re.search(pattern2, bytecode)
    if group is not None:
        bytecode = bytecode[group.start() + 4:]
    return bytecode

def getDisasm(runtimeCode):
    if "0x" in runtimeCode:
        runtimeCode = runtimeCode[2:]
    path = "./tmp/bytocode"
    with open(path, 'w') as file:
        file.write(runtimeCode)
    try:
        disasmP = subprocess.Popen(
            ["evm", "disasm", path], stdout=subprocess.PIPE
        )
        disasmOut = disasmP.communicate()[0].decode('utf-8', 'strict')
    except:
        logging.critical("Disassembly failed.")
        os.remove(path)
        exit()
    os.remove(path)
    return disasmOut

def getInstructions(disasm):
    instructions = {}
    lines = disasm.split("\n")[1:-1]
    for line in lines:
        if "opcode" in line:
            break
        tmp = line.split(": ")
        lineID = int(tmp[0], 16)
        instructions[lineID] = tmp[1]
    return instructions

def constructBasicBlocks(instructions):
    if len(instructions) == 0:
        return {}
    block = BasicBlock()
    block_instructions = {}
    basicBlocks = {}
    first = True
    start = True
    lastPos = -1
    for key, value in instructions.items():
        pos = key
        op_code = value.split(" ")[0]
        # block_instructions[key] = value
        if start or op_code == "JUMPDEST":
            if first:
                first = False
            else:
                block.setEnd(lastPos)
                block.setInstructions(block_instructions)
                basicBlocks[block.getStart()] = block
            block = BasicBlock()
            block.setStart(pos)
            block_instructions = {}
            start = False
        elif op_code == "JUMPI":
            start = True
            block.setJumpType(2)
        elif op_code == "JUMP":
            start = True
            block.setJumpType(1)
        if op_code in ["STOP", "RETURN", "REVERT", "SELFDESTRUCT", "INVALID"]:
            start = True
            block.setJumpType(3)
        block_instructions[key] = value
        lastPos = pos
    block.setEnd(lastPos)
    block.setInstructions(block_instructions)
    basicBlocks[block.getStart()] = block
    return basicBlocks

def addFallsTo(basicBlocks):
    keys = list(basicBlocks.keys())
    for i in range(len(keys)):
        if basicBlocks[keys[i]].getJumpType() in [0, 2] and i < len(keys) - 1:
            basicBlocks[keys[i]].setFallsTo(keys[i + 1])

def getFunctionBlock(basicBlocks):
    functionBlocks = {}
    for _, block in basicBlocks.items():
        instructions = block.getInstructions()
        keys = list(instructions.keys())
        length = len(keys)
        # if instructions[keys[0]] != "JUMPDEST":
        if len(keys) >= 5:
            if "DUP1" in instructions[keys[length - 5]] and "PUSH" in instructions[keys[length - 4]] and instructions[keys[length - 3]] == "EQ" and "PUSH" in instructions[keys[length - 2]] and instructions[keys[length - 1]] == "JUMPI":
                functionBlocks[instructions[keys[length - 4]].split(" ")[1]] = int(instructions[keys[length - 2]].split(" ")[1], 16)
        if len(keys) >= 5:
            if "PUSH" in instructions[keys[length - 5]] and "DUP2" in instructions[keys[length - 4]] and instructions[keys[length - 3]] == "EQ" and "PUSH" in instructions[keys[length - 2]] and instructions[keys[length - 1]] == "JUMPI":
                functionBlocks[instructions[keys[length - 5]].split(" ")[1]] = int(instructions[keys[length - 2]].split(" ")[1], 16)
    return functionBlocks

def getFallback(block):
    instructions = block.getInstructions()
    keys = list(instructions.keys())
    length = len(keys)
    if "CALLDATASIZE" in instructions[keys[length - 4]] and "PUSH" in instructions[keys[length - 2]] and instructions[keys[length - 1]] == "JUMPI":
        return int(instructions[keys[length - 2]].split(" ")[1], 16)
    else:
        return None