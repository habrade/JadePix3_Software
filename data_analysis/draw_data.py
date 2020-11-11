#!/usr/bin/env python3

import coloredlogs
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"

data_file = "../data/data.txt"

data_ch0 = []
data_ch1 = []
data_ch2 = []
data_ch3 = []

tail = []
head = []
error = []

num_total = 0
oc = 0  # Overflow counter
rbof = 0  # Ring buffer overflow
fifo_status = 0
frame_index = 0
frame_index_lst = []
rbof_lst = []
oc_lst = []
error_lst = []
error_num = 0

data_num = 0
data_num_lst = []

num_at_head = 0

last_head_ptr = 0
last_tail_ptr = 0

# Decode Data
fo = open(data_file, "r")
for frame_hex_string in fo.readlines():
    num_total += 1

    frame_hex_string = frame_hex_string.strip()
    frame_data = int(frame_hex_string, 16)
    frame_type = (frame_data >> 23)

    if frame_type == 0:  # Tail
        last_tail_ptr = num_total
        frame_index = frame_data
        frame_index_lst.append(frame_index)
        log.info("Frame tail at Line: {:d}, Frame Index: {:d}".format(num_total, frame_index))
        num_in_frame = num_total - num_at_head - 1
        log.info("Data number in this frame: {:d}".format(num_in_frame))
        log.info("Data overflow: {:d}".format(oc))
        data_num_lst.append(data_num)
        oc_lst.append(oc)
        tail.append(frame_data)
        error_lst.append(error_num)
    elif frame_type == 1:  # Head
        last_head_ptr = num_total
        if last_head_ptr != (last_tail_ptr + 1) and frame_index != 0:
            log.error("Frame flag missed!")
        fifo_status = (frame_data >> 15) & 0xFF
        rbof += frame_data & 0x7FFF
        rbof_lst.append(rbof)
        log.info("FIFO status: {:08b}, RBOF: {:d}".format(fifo_status, rbof))
        num_at_head = num_total
        log.info("\nFrame head at Line: {:d}".format(num_total))
        head.append(frame_data)
    elif frame_type == 2:  # Data
        data_num += 1
        ch = (frame_data >> 16) & 0x3
        oc += (frame_data >> 18) & 0x1F
        if ch == 0:  # Ch 0
            data_ch0.append(frame_data)
        elif ch == 1:  # Ch 1
            data_ch1.append(frame_data)
        elif ch == 2:  # Ch 2
            data_ch2.append(frame_data)
        elif ch == 3:  # Ch 3
            data_ch3.append(frame_data)
    elif frame_type == 3:  # Error
        error_num += 1
        error.append(frame_data)
fo.close()

log.info("\nNumbers:")
log.info("\tTotal: {:d}".format(num_total))
log.info("\tRBOF : {:d}".format(rbof))
log.info("\tHead: {:d}".format(len(head)))
log.info("\tTail: {:d}".format(len(tail)))

data = [data_ch0, data_ch1, data_ch2, data_ch3]
num_data_ch = []
num_data = 0
for i in range(4):
    num_data_ch.append(len(data[i]))
    num_data += num_data_ch[i]
    log.info("\tData in channel {:d}: {:d}".format(i, len(data[i])))
log.info("\tGot data: {:d}".format(num_data))

log.info("\tOverflow Counter: {:d}".format(oc))

import matplotlib.pyplot as plt

plt.plot(frame_index_lst, oc_lst, marker='o', label="FIFO overflow")
plt.plot(frame_index_lst, data_num_lst, marker='+', label="Data")
plt.plot(frame_index_lst, rbof_lst, marker='s', label="Ring buffer overflow")
plt.plot(frame_index_lst, error_lst, marker='', label="IPbus FIFO overflow")
plt.xlabel('Frame Index')
plt.ylabel('Numbers')
plt.legend()
plt.grid(True)
plt.show()
