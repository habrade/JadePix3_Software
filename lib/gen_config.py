#!/usr/bin/env python3
import csv

from lib import jadepix_defs

def gen_config(data_file):

    with open(data_file, 'w+', newline='') as csvfile:
        config_writer = csv.writer(csvfile, delimiter=' ',
                                   quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        
        CON_SELM = 1
        CON_SELP = 1
        CON_DATA = 1
        for i in range(jadepix_defs.ROW * jadepix_defs.COL):
            config_writer.writerow([CON_SELM, CON_SELP, CON_DATA])

    with open(data_file, newline='') as csvfile:
        config_reader = csv.reader(csvfile, delimiter=' ', quotechar=' ')
        for row in config_reader:
            pass

if __name__ == "__main__":
    data_file = "etc/config/config.csv"
    gen_config(data_file)