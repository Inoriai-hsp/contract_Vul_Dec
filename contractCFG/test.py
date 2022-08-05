# import graphviz  
# dot = graphviz.Digraph(comment='The Round Table')
# dot.attr('node', shape='cube')
# dot.node('A', 'King Arthur')  
# dot.node('B', '''<<TD>Sir Bedevere<BR ALIGN="LEFT"/>the Wise</TD>>''')
# dot.node('L', 'Sir Lancelot the Brave')

# dot.edges(['AB', 'AL'])
# dot.edge('B', 'L', constraint='false')
# dot.view()

# with open("/home/huangshiping/data/blocks/unique_blocks.txt", "r") as f:
#     length = 0
#     for line in f.readlines():
#         block = line.strip().split(' ')
#         if len(block) > length:
#             length = len(block)
#             if length > 256:
#                 print(length)
#     print(length)

import os
dirs = os.listdir("/home/huangshiping/data/cfgs_new2")
print(len(dirs))