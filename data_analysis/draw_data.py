data_file = "../data/data.txt"

data_ch0 = []
data_ch1 = []
data_ch2 = []
data_ch3 = []

tail = []
head = []
error = []

# Decode Data
fo = open(data_file, "r")
for data in fo.readlines():
    data = data.strip()
    flag = (int(data, 16) >> 23) & 0b11
    if flag == 0:  # Tail
        tail.append(data)
    elif flag == 1:  # Head
        head.append(data)
    elif flag == 2:  # Data
        ch = (int(data, 16) >> 16) & 0b11
        if ch == 0:  # Ch 0
            data_ch0.append(data)
        elif ch == 1:  # Ch 1
            data_ch1.append(data)
        elif ch == 2:  # Ch 2
            data_ch2.append(data)
        elif ch == 3:  # Ch 3
            data_ch3.append(data)
    elif flag == 3:  # Error
        error.append(data)
fo.close()
