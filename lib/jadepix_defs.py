from bitarray import bitarray

## Pix chip parameters
ROW = 512
COL = 192

## SPI config
idac1_data = bitarray("11100000")
idac2_data = bitarray("11111111")
idac3_data = bitarray("11111111")
idac4_data = bitarray("11111111")
idac5_data = bitarray("11111111")
idac6_data = bitarray("11111111")
moni_sel_idac1 = bitarray("1")
moni_sel_idac2 = bitarray("1")
moni_sel_idac3 = bitarray("1")
moni_sel_idac4 = bitarray("1")
moni_sel_idac5 = bitarray("1")
moni_sel_idac6 = bitarray("1")

vdac1_data = bitarray("1111111111")
vdac2_data = bitarray("1111111111")
vdac3_data = bitarray("1111111111")
vdac4_data = bitarray("1111111111")
vdac5_data = bitarray("1111111111")
vdac6_data = bitarray("1111111111")
moni_sel_vdac1 = bitarray("1")
moni_sel_vdac2 = bitarray("1")
moni_sel_vdac3 = bitarray("1")
moni_sel_vdac4 = bitarray("1")
moni_sel_vdac5 = bitarray("1")
moni_sel_vdac6 = bitarray("1")

bgp_en = bitarray("1")
bgp_trim = bitarray("1111")
rsds_sel_lpbk = bitarray("1")
rsds_sel_rx = bitarray("1")
rsds_sel_tx = bitarray("1")
pll_rbit0 = bitarray("1")
pll_rbit1 = bitarray("1")
pll_ibit1 = bitarray("1")
pll_ibit0 = bitarray("1")
