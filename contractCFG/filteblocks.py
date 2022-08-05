
if __name__ == "__main__":
    blocks = []
    for index in range(10):
        with open("/home/huangshiping/data/blocks/blocks" + str(index) + ".txt", "r") as f:
            block = list(set(list(f.readlines())))
            # print(block[-1])
            blocks.extend(block)

    unique_blocks = list(set(blocks))
    with open("/home/huangshiping/data/blocks/unique_blocks.txt", "a") as f:
        f.writelines(unique_blocks)
    print(len(unique_blocks))
    print("done!")