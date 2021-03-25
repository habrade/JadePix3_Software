mkdir -p Output
mkdir -p Logfiles

for i in $(seq 595 615); do
    ./Analyze_Jadepixtxt.py  -i ../data/data_rs_0325_y5${i}.txt   -o Output/test_rs_0325_y5${i}.root -y 5.${i} > Logfiles/log_0325_y5${i}  2>&1&
done
