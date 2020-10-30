#!/usr/bin/env python3

data_file = "../data/data.txt"

data_ch0 = []
data_ch1 = []
data_ch2 = []
data_ch3 = []

tail = []
head = []
error = []

num_totoal = 0
oc = 0
rbof = 0

# Decode Data
fo = open(data_file, "r")
for frame_hex_string in fo.readlines():
    num_totoal += 1
    frame_hex_string = frame_hex_string.strip()
    frame_data = int(frame_hex_string, 16)
    frame_type = (frame_data >> 23) & 0b11
    if frame_type == 0:  # Tail
        tail.append(frame_hex_string)
    elif frame_type == 1:  # Head
        rbof += frame_data & 
        head.append(frame_hex_string)
    elif frame_type == 2:  # Data
        oc += (frame_data >> 18) & 0b11
        ch = (int(frame_hex_string, 16) >> 16) & 0b11
        if ch == 0:  # Ch 0
            data_ch0.append(frame_hex_string)
        elif ch == 1:  # Ch 1
            data_ch1.append(frame_hex_string)
        elif ch == 2:  # Ch 2
            data_ch2.append(frame_hex_string)
        elif ch == 3:  # Ch 3
            data_ch3.append(frame_hex_string)
    elif frame_type == 3:  # Error
        error.append(frame_hex_string)
fo.close()

print("Numbers:")
print("\tTotal: {:d}".format(num_totoal))
print("\tHead: {:d}".format(len(head)))
print("\tTail: {:d}".format(len(tail)))

data = [data_ch0, data_ch1, data_ch2, data_ch3]
num_data_ch = []
num_data = 0
for i in range(4):
    num_data_ch.append(len(data[i]))
    num_data += num_data_ch[i]
    print("\tData in channel {:d}: {:d}".format(i, len(data[i])))
print("\tGot data: {:d}".format(num_data))

print("\tOverflow Conter: {:d}".format(oc))
