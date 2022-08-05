import sent2vec
import json
import os
import numpy as np
model = sent2vec.Sent2vecModel()
model.load_model('model.bin') # The model can be sent2vec or cbow-c+w-ngrams

contract_files = os.listdir("/home/huangshiping/data/cfgs_new2")
index = 0
for contract_file in contract_files:
    index += 1
    cfgs = {}
    with open("/home/huangshiping/data/cfgs_new2/" + contract_file, "r") as f:
        contract = json.load(f)
        blocks = contract['blocks']
        for block_number in list(blocks.keys()):
            blocks[block_number] = model.embed_sentence(blocks[block_number])
        function_cfgs = contract['function_cfgs']
        for function in list(function_cfgs.keys()):
            function_cfg = function_cfgs[function]
            node = list(function_cfg.keys())
            x = []
            for key in node:
                x.append(blocks[key][0])
            x = np.array(x)
            pre = []
            next = []
            for i in range(0, len(node)):
                for key in function_cfg[node[i]]['next']:
                    pre.append(i)
                    next.append(node.index(str(key)))
            edges = np.array([pre, next], dtype=np.int32)
            cfgs[function] = {"x": x.tolist(), "edges": edges.tolist()}
    with open("/home/huangshiping/data/cfg_embeddings/" + contract_file, "w") as f:
        f.write(json.dumps(cfgs))
    print(index)
print("done!")