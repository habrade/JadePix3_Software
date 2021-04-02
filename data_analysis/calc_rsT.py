#!/usr/bin/env python3

#import ROOT
import numpy as np

data_file = "data/data_rs.txt" 

ROW = 512
PULSE_PERIOD = 500 # Unit: us
RS_PERIOD = 192 # Unit: ns
FRAME_NUMBER_SET=40000

x = []
y = []

pulse_index = 0
row_loc = 0
pulse_loc = .0

with open(data_file,'r') as fin:
	lines = fin.readlines()
	framenumber = 0
	pulse_index = 0
	framestart = True
	frameend = False

	for line in lines:

		raw16 = int(line, 16)
		flag = (raw16 >> 30)

		if flag == 1:  # Frame Head
			framestart = True
		elif flag == 0 : # Frame tail
			frameend = True
			#framestart = False
			if row_loc > 0:
				pulse_loc = raw16 + float(row_loc/ROW)
				pulse_index += 1
				x.append(pulse_index)
				y.append(pulse_loc)
		elif flag == 2: # Frame Data
			sec = (raw16 >> 16) & 0x3 #0-3
			data = (raw16 & 0xFFFF)
			datarow = (data >> 7) #0-511
			datablk = (data >> 3) & 0xF #0-15

			if framestart:
				row_loc = datarow
			
			framestart = False
			
import matplotlib.pyplot as plt
slope, intercept = np.polyfit(x, y, 1)
rs_period = PULSE_PERIOD/slope
print(slope)
print(intercept)
print("RS Period: {:}".format(rs_period))

plt.scatter(x, y, marker='o', color="black")
plt.text(10000, 350000, r'Slope = {:.5}'.format(slope))
plt.text(10000, 320000, r'RS Period = {:.5} us'.format(rs_period))
plt.xlabel('Pulse Index')
plt.ylabel('Pulse Location/Frame number')
plt.grid(False)

print("{} {}".format(x[len(x)-1], x[0]))
print("{} {}".format(y[len(x)-1], y[0]))

linear_model=np.polyfit(x,y,1)
linear_model_fn=np.poly1d(linear_model)
x_s=np.arange(0,78370)
plt.plot(x_s,linear_model_fn(x_s),color="red")

#plt.show()
plt.savefig("calc_rs.png")


