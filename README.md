### JadePix3 Software

Note: Python3 is needed

#### Install libraries and requirements
```shell script
pip3 install -e .
pip3 install -r requirements.txt
```

#### Run
1. SPI configuration
    * The location of configuration file: __lib/jadepix_defs.py__. Consider to change the style be more general, eg, *.ini, *.json
2. JadePix configuration
    * The location of configuraiton file: __config/jadepix_config.txt__ 

3. Dump data:
```shell script
. setEnv.sh
./run.py
```

4. Plot data:
```shell script
python3 data_analysis/data_analysis.py
```