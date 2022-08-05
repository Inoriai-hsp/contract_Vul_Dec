from torch_geometric.data import Data
from tqdm import tqdm
import random
import pandas as pd
import torch
import json

def getData(num_cfg):
    datas = pd.read_csv("/home/huangshiping/data/contractLabels.csv")
    contracts = []
    for row in tqdm(range(0, datas.shape[0])):
        address = datas.loc[row, 'address']
        reentrancy = datas.loc[row, 'reentrancy']
        with open("/home/huangshiping/data/cfg_embeddings/" + address + ".json", "r") as f:
            cfg = json.load(f)
            # print(cfg)
            x = []
            edge_index = [[], []]
            slices = []
            index = 0
            for graph in list(cfg.values()):
                edge_index[0].extend([i + len(x) for i in graph['edges'][0]])
                edge_index[1].extend([i + len(x) for i in graph['edges'][1]])
                x.extend(graph['x'])
                slices.extend([ index for n in range(len(graph['x']))])
                index += 1
            if len(x) == 0:
                continue
            mask = [False for n in range(0, len(cfg))]
            for i in range(0, num_cfg - len(cfg)):
                x.append(0 for n in range(0, len(x[0])))
                slices.append(slices[-1] + 1)
                mask.append(True)
            # data = {}
            # data["x"] = x
            # data["y"] = [reentrancy]
            # data["edge_index"] = edge_index
            # data["slices"] = slices
            # data["num_cfg"] = num_cfg
            # data["mask"] = mask
            # contracts[address] = data
            data = Data(x=torch.tensor(x, dtype=torch.float32), y = torch.tensor([reentrancy], dtype=torch.int64), edge_index=torch.tensor(edge_index, dtype=torch.int64))
            data.slices = torch.tensor(slices, dtype=torch.int64)
            data.num_cfg = num_cfg
            data.mask = torch.tensor(mask, dtype=torch.bool)
            contracts.append(data)
    # return contracts
    torch.save(contracts, "./data/contracts.pkl")
    # with open("./data/contracts.json", "w") as f:
    #     f.write(json.dump(contracts))

def loadData(contracts, batch_size, shuffle=False):
    if shuffle:
        random.shuffle(contracts)
    batchs = [i for i in range(0, len(contracts), batch_size)]
    batchs.append(len(contracts))
    loaders = []
    for i in range(1, len(batchs)):
        batch = contracts[batchs[i-1]:batchs[i]]
        # print(batch)
        x = torch.tensor([], dtype=torch.float32)
        y = torch.tensor([], dtype=torch.int64)
        num_cfgs = 0
        num_contracts = 0
        mask = torch.tensor([], dtype=torch.bool)
        batch_index = torch.tensor([], dtype=torch.int64)
        edge_index = torch.tensor([], dtype=torch.int64)
        for data in batch:
            data_x = data.x
            data_y = data.y
            data_mask = data.mask
            data_edge_index = data.edge_index
            data_slices = data.slices
            # print(data_slices[-1])
            num_cfg = data.num_cfg
            batch_index = torch.cat([batch_index, data_slices + num_cfgs])
            # print(batch_index[-1])
            num_cfgs += num_cfg
            num_contracts += 1
            mask = torch.cat([mask, data_mask.view(1, -1)])
            edge_index = torch.cat([edge_index, data_edge_index + x.shape[0]], dim=1)
            # print(edge_index[0][-1])
            x = torch.cat([x, data_x])
            # print(x.shape)
            y = torch.cat([y, data_y])
            # print(y.shape)
        loader = Data(x=x, y=y, edge_index=edge_index)
        loader.num_contracts = num_contracts
        loader.batch_index = batch_index
        loader.mask = mask
        loaders.append(loader)
    return loaders

# datas = pd.read_csv("/home/huangshiping/data/contractLabels.csv")
# num_cfg = 0
# for row in tqdm(range(0, datas.shape[0])):
#     address = datas.loc[row, 'address']
#     reentrancy = datas.loc[row, 'reentrancy']
#     with open("/home/huangshiping/data/cfg_embeddings/" + address + ".json", "r") as f:
#         cfg = json.load(f)
#         if len(cfg) > num_cfg:
#             num_cfg = len(cfg)
# print(num_cfg)

# getData(256)
# contracts = torch.load("./data/contracts.pkl")
# print(len(contracts))