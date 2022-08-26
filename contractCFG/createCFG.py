from copy import deepcopy
import json
from tqdm import tqdm
# import os
from util import *
from evm import *
import sys  # 导入sys模块
sys.setrecursionlimit(6000)  # 将默认的递归深度修改为3000

# bb_count = {}
block_count = {}
function_cfg = {}
basicBlocks = {}
coverage_count = {}

def excuteBlock(block, evm):
    # print(block.getStart())
    # if block.getStart() == 5215:
    #     print(2112)
    global basicBlocks, block_count, function_cfg, coverage_count
    if block_count[block.getStart()] >= 10:
        return
    else:
        block_count[block.getStart()] += 1
    if coverage_count[block.getStart()] == 0:
        coverage_count[block.getStart()] = 1
    # bb_count[block.getStart()] += 1
    instructions = block.getInstructions()
    instrs = list(instructions.values())
    for i in range(0, len(instrs) - 1):
        instr = instrs[i].split(" ")
        if "DUP" in instr[0]:
            number = int(instr[0][3:], 10)
            evm.DUP(number)
        elif "SWAP" in instr[0]:
            number = int(instr[0][4:], 10)
            evm.SWAP(number)
        elif "LOG" in instr[0]:
            number = int(instr[0][3:], 10)
            evm.LOG(number)
        elif "PUSH" in instr[0]:
            number = int(instr[0][4:], 10)
            evm.PUSH(number, instr[1])
        else:
            excuteInstr = getattr(evm, instr[0])
            excuteInstr()
        # print(instr[0])
    instr = instrs[-1].split(" ")
    if "DUP" in instr[0]:
        number = int(instr[0][3:], 10)
        evm.DUP(number)
    elif "SWAP" in instr[0]:
        number = int(instr[0][4:], 10)
        evm.SWAP(number)
    elif "LOG" in instr[0]:
        number = int(instr[0][3:], 10)
        evm.LOG(number)
    elif "PUSH" in instr[0]:
        number = int(instr[0][4:], 10)
        evm.PUSH(number, instr[1])
    elif instr[0] == "JUMPI":
        target, flag = evm.JUMPI()
        if isReal(flag):
            if flag == 0:
                fallsTo = block.getFallsTo()
                block_fall = basicBlocks[fallsTo]
                evm_fall = evm
                evm_fall.setPc(fallsTo)
                if fallsTo not in function_cfg[block.getStart()]["next"]:
                    function_cfg[block.getStart()]["next"].append(fallsTo)
                if block.getStart() not in function_cfg[fallsTo]["pre"]:
                    function_cfg[fallsTo]["pre"].append(block.getStart())
                excuteBlock(block_fall, evm_fall)
            elif target in list(basicBlocks.keys())[1:]:
                if target not in function_cfg[block.getStart()]["next"]:
                    function_cfg[block.getStart()]["next"].append(target)
                evm_target = deepcopy(evm)
                evm_target.setPc(target)
                block_target = basicBlocks[target]
                if block.getStart() not in function_cfg[target]["pre"]:
                    function_cfg[target]["pre"].append(block.getStart())
                excuteBlock(block_target, evm_target)
        else:
            if target in list(basicBlocks.keys())[1:]:
                if target not in function_cfg[block.getStart()]["next"]:
                    function_cfg[block.getStart()]["next"].append(target)
                evm_target = deepcopy(evm)
                evm_target.setPc(target)
                block_target = basicBlocks[target]
                if block.getStart() not in function_cfg[target]["pre"]:
                    function_cfg[target]["pre"].append(block.getStart())
                excuteBlock(block_target, evm_target)
            fallsTo = block.getFallsTo()
            block_fall = basicBlocks[fallsTo]
            evm_fall = evm
            evm_fall.setPc(fallsTo)
            if fallsTo not in function_cfg[block.getStart()]["next"]:
                function_cfg[block.getStart()]["next"].append(fallsTo)
            if block.getStart() not in function_cfg[fallsTo]["pre"]:
                function_cfg[fallsTo]["pre"].append(block.getStart())
            excuteBlock(block_fall, evm_fall)
    elif instr[0] == "JUMP":
        target = evm.JUMP()
        if target == None or target == 0:
            return
        if target in list(basicBlocks.keys()):
            if target not in function_cfg[block.getStart()]["next"]:
                function_cfg[block.getStart()]["next"].append(target)
            evm_target = deepcopy(evm)
            evm_target.setPc(target)
            block_target = basicBlocks[target]
            if block.getStart() not in function_cfg[target]["pre"]:
                function_cfg[target]["pre"].append(block.getStart())
            excuteBlock(block_target, evm_target)
    else:
        excuteInstr = getattr(evm, instr[0])
        excuteInstr()
    if block.getFallsTo() != -1 and instr[0] not in ["JUMP", "JUMPI"]:
        fallsTo = block.getFallsTo()
        block_fall = basicBlocks[fallsTo]
        evm_fall = evm
        evm_fall.setPc(fallsTo)
        if fallsTo not in function_cfg[block.getStart()]["next"]:
            function_cfg[block.getStart()]["next"].append(fallsTo)
        if block.getStart() not in function_cfg[fallsTo]["pre"]:
            function_cfg[fallsTo]["pre"].append(block.getStart())
        excuteBlock(block_fall, evm_fall)

def getBlockJson(basicBlocks):
    blocks = {}
    for number, block in basicBlocks.items():
        instructions = block.getInstructions()
        item = ''
        instrs = list(instructions.values())
        for i in range(0, len(instrs) - 1):
            item = item + instrs[i].split(' ')[0] + ' '
        item = item + instrs[-1].split(' ')[0]
        blocks[number] = item
    return blocks

def getCoverage(coverage_count):
    visit_number = 0
    for block in list(coverage_count.values()):
        visit_number += block
    return visit_number / len(coverage_count)

def getCFG(byte):
    global basicBlocks, block_count, function_cfg, coverage_count
    block_count = {}
    function_cfg = {}
    basicBlocks = {}
    contract_cfg = {}
    function_cfgs = {}
    coverage_count = {}
    bytecode = readRuntimeCode(byte)
    disasm = getDisasm(bytecode)
    # print(disasm)
    instructions = getInstructions(disasm)
    instrFormat(instructions)
    basicBlocks = constructBasicBlocks(instructions)
    # filteBlocks(basicBlocks)
    for key in basicBlocks.keys():
        coverage_count[key] = 0
    blocks = getBlockJson(basicBlocks)
    # print(blocks)
    contract_cfg['blocks'] = blocks
    # outputBlocks(basicBlocks, "./blocks/blocks1.txt")
    addFallsTo(basicBlocks)
    functionBlocks = getFunctionBlock(basicBlocks)
    fallback_block = getFallback(basicBlocks[0])
    if fallback_block is not None:
        for key in basicBlocks.keys():
            block_count[key] = 0
            function_cfg[key] = {"pre": [], "next": []}
        block = basicBlocks[fallback_block]
        evm = EVM([], fallback_block)
        excuteBlock(block, evm)
        filteCfg(function_cfg, fallback_block)
        function_cfgs['fallback'] = deepcopy(function_cfg)
    # for key in basicBlocks.keys():
    #         bb_count[key] = 0
    for function_sig, blockNumber in functionBlocks.items():
        for key in basicBlocks.keys():
            block_count[key] = 0
            function_cfg[key] = {"pre": [], "next": []}
        block = basicBlocks[blockNumber]
        evm = EVM([int(function_sig, 16)], blockNumber)
        try:
            excuteBlock(block, evm)
        except Exception as e:
            if isinstance(e, ValueError) and e.args[0] == "STACK underflow":
                continue
            else:
                raise e
        filteCfg(function_cfg, blockNumber)
        function_cfgs[function_sig] = deepcopy(function_cfg)
        # generateGraph(basicBlocks, function_cfg, function_sig)
    if len(functionBlocks) == 0 and fallback_block is None:
        for key in basicBlocks.keys():
            block_count[key] = 0
            function_cfg[key] = {"pre": [], "next": []}
        block = basicBlocks[0]
        evm = EVM([], 0)
        excuteBlock(block, evm)
        filteCfg(function_cfg, 0)
        function_cfgs['fallback'] = deepcopy(function_cfg)
    contract_cfg['function_cfgs'] = function_cfgs
    contract_cfg['block_visit'] = coverage_count
    contract_cfg['block_coverage'] = getCoverage(coverage_count)
    return contract_cfg
    # print("done!")

if __name__ == "__main__":
    with open("/home/huangshiping/data/bytecodes_47398.txt", "r") as f:
        lines = f.readlines()
        print(len(lines))
        for i in tqdm(range(0, len(lines))):
            address = lines[i].split('\n')[0].split(':')[0]
            byte = lines[i].split('\n')[0].split(':')[1]
            try:
                contract_cfg = getCFG(byte)
                contract_cfg['address'] = address
                with open("/home/huangshiping/data/cfgs_new3/" + address + ".json", "w") as f:
                    f.write(json.dumps(contract_cfg))
                if len(contract_cfg['function_cfgs']) == 0:
                    with open("/home/huangshiping/data/no_funcs.txt", "a") as f:
                        f.write(str(i) + ":" + address + "\n")
            except Exception as e:
                with open("/home/huangshiping/data/error_cfgs3.txt", "a") as f:
                    f.write(str(i) + ":" + address + "\n")
            # print(str(i))
        # for line in lines:
        #     address = line.split('\n')[0].split(':')[0]
        #     byte = line.split('\n')[0].split(':')[1]
        #     if address == "0x0148179f1ff77e236e97b646502261ea29517d32":
                # contract_cfg = getCFG(byte)
        # with open("/home/huangshiping/data/cfgs_new2/" + address + ".json", "w") as f:
        #     f.write(json.dumps(contract_cfg))
    # byte_file = open("/home/huangshiping/data/bytecodes.txt", "r")
    # bytecodes = byte_file.readlines()
    # with open("/home/huangshiping/data/errors.txt", "r") as f:
    #     lines = f.readlines()
    #     for line in lines:
    #         index = int(line.split('\n')[0].split(':')[0])
    #         address = line.split('\n')[0].split(':')[1]
    #         bytecode = bytecodes[index]
    #         if address == bytecode.split('\n')[0].split(':')[0]:
    #             byte = bytecode.split('\n')[0].split(':')[1]
    #             try:
    #                 contract_cfg = getCFG(byte)
    #                 contract_cfg['address'] = address
    #                 with open("/home/huangshiping/data/cfgs/" + address + ".json", "w") as f:
    #                     f.write(json.dumps(contract_cfg))
    #             except Exception as e:
    #                 with open("/home/huangshiping/data/errors_again.txt", "a") as f:
    #                     f.write(str(index) + ":" + address + "\n")
    #         else:
    #             with open("/home/huangshiping/data/errors_match.txt", "a") as f:
    #                 f.write(str(index) + ":" + address + "not match" + "\n")
    #         print(str(index))
    # byte_file.close()
    # dirs = os.listdir("/home/huangshiping/data/cfgs")
    # print(len(dirs))
    print("done!")