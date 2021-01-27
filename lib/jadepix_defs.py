from bitarray import bitarray

## Pix chip parameters
ROW = 512
COL = 192
BLK = 4

SYS_CLK_PERIOD = 12  # Unit: ns

## SPI config
idac1_data = bitarray("10000000")
idac2_data = bitarray("00101010")
idac3_data = bitarray("10000000")
idac4_data = bitarray("10000000")
idac5_data = bitarray("10000000")
idac6_data = bitarray("10000000")

# TODO: only one can available
moni_sel_idac1 = bitarray("0")
moni_sel_idac2 = bitarray("0")
moni_sel_idac3 = bitarray("0")
moni_sel_idac4 = bitarray("0")
moni_sel_idac5 = bitarray("0")
moni_sel_idac6 = bitarray("0")

vdac1_data = bitarray("0100011001")
vdac2_data = bitarray("0100011001")
vdac3_data = bitarray("0110100101")
vdac4_data = bitarray("0100011001")
vdac5_data = bitarray("0101011111")
vdac6_data = bitarray("0000000000")

# TODO: only one can available
moni_sel_vdac1 = bitarray("0")
moni_sel_vdac2 = bitarray("0")
moni_sel_vdac3 = bitarray("0")
moni_sel_vdac4 = bitarray("0")
moni_sel_vdac5 = bitarray("0")
moni_sel_vdac6 = bitarray("0")

bgp_en = bitarray("1")
bgp_trim = bitarray("1101")
rsds_sel_lpbk = bitarray("0")
rsds_sel_rx = bitarray("0")
rsds_sel_tx = bitarray("0")
pll_rbit0 = bitarray("0")
pll_rbit1 = bitarray("0")
pll_ibit1 = bitarray("0")
pll_ibit0 = bitarray("1")
