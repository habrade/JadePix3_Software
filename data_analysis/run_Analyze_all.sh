mkdir -p Logfiles
mkdir -p Outfiles

for i in $(seq 10 28); do
    ftag="7${i}"
    ./Analyze_Jadepixtxt.py  -i ../data/data_rs_0325_x0${ftag}.txt   -o Outfiles/test_0325_x0${ftag}.root -x 0.${ftag} > Logfiles/log_0325_x0${ftag}  2>&1&
done


for i in $(seq 0 9); do
    ftag="70${i}"
    ./Analyze_Jadepixtxt.py  -i ../data/data_rs_0325_x0${ftag}.txt   -o Outfiles/test_0325_x0${ftag}.root -x 0.${ftag} > Logfiles/log_0325_x0${ftag}  2>&1&
done
