#!/usr/bin/env python3

oc_lst = []

data_file = "data/data_rs.txt"
with open(data_file, 'r') as data_file:
    lines = data_file.readlines()
    for line in lines:
        data = int(line, 16)
        if data > 0x0103ffff:
            oc_lst.append(data_file)
    print(oc_lst)
    
data_oc = "data/data_oc.txt"
with open(data_oc, "w+") as f_w:
    data_string = []
    for data in oc_lst:
        data_string.append("{:#010x}\n".format(data))
        data_file.write("".join(data_string))

