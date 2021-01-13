#!/usr/bin/env python3
import csv

from lib import jadepix_defs


def gen_config(data_file, config, is_mask, sel_mask_en, sel_pulse_en, sel_row, sel_col, sel_data):
    with open(data_file, 'w+', newline='') as csvfile:
        config_writer = csv.writer(csvfile, delimiter=' ',
                                   quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        CON_SELM = config[0]
        CON_SELP = config[1]
        CON_DATA = config[2]

        for i in range(jadepix_defs.ROW * jadepix_defs.COL):
            if is_mask:
                if sel_mask_en:
                    if i == (sel_row * jadepix_defs.COL + sel_col):
                        CON_DATA = sel_data
                    else:
                        CON_DATA = config[2]

            elif sel_pulse_en:
                if i == (sel_row * jadepix_defs.COL + sel_col):
                    CON_DATA = sel_data
                else:
                    CON_DATA = config[2]

            config_writer.writerow([CON_SELM, CON_SELP, CON_DATA])

    # with open(data_file, newline='') as csvfile:
    #     config_reader = csv.reader(csvfile, delimiter=' ', quotechar=' ')
    #     for row in config_reader:
    #         pass


if __name__ == "__main__":
    data_file = "etc/config/config.csv"
    gen_config(data_file)
