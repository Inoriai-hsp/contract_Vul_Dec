from util import *
import json
# import multiprocessing

# def byteToBlocks(byte, number):
#     bytecode = readRuntimeCode(byte)
#     disasm = getDisasm(bytecode)
#     # print(disasm)
#     instructions = getInstructions(disasm)
#     # print(instructions)
#     instrFormat(instructions)
#     basicBlocks = constructBasicBlocks(instructions)
#     filteBlocks(basicBlocks)
#     outputBlocks(basicBlocks, "/home/huangshiping/data/blocks/blocks" + str(number) + ".txt")

# def readFromFile(number):
#     print("number:" + str(number))
#     path = '/home/huangshiping/data/bytecodes/bytecodes' + str(number) + '.json'
#     index = 0
#     with open(path, 'r') as f:
#         line = f.readline()
#         while(line):
#             bytecode = json.loads(line)['bytecode']
#             # print(bytecode)
#             byteToBlocks(bytecode, number)
#             print(index)
#             line = f.readline()
#             index += 1

# if __name__ == "__main__":
#     # pool = multiprocessing.Pool(10)
#     for number in range(0, 10):
#         readFromFile(number)
#     # pool.close()
#     # pool.join()

def byteToBlocks(byte):
    bytecode = readRuntimeCode(byte)
    disasm = getDisasm(bytecode)
    # print(disasm)
    instructions = getInstructions(disasm)
    # print(instructions)
    instrFormat(instructions)
    basicBlocks = constructBasicBlocks(instructions)
    filteBlocks(basicBlocks)
    outputBlocks(basicBlocks, "/home/huangshiping/data/blocks_47398.txt")

with open("/home/huangshiping/data/bytecodes_47398.txt", "r") as f:
    lines = f.readlines()
    for line in lines:
        bytecode = line.strip().split(':')[1]
        byteToBlocks(bytecode)
    print("done!")