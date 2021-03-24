for i in $(seq 10 30); do
    ftag="7${i}"
    ./Analyze_Jadepixtxt.py  -i ../data/data_rs_x0${ftag}.txt   -o test_x0${ftag}.root -x 0.${ftag} > log_x0${ftag}  2>&1&
done


for i in $(seq 0 9); do
    ftag="70${i}"
    ./Analyze_Jadepixtxt.py  -i ../data/data_rs_x0${ftag}.txt   -o test_x0${ftag}.root -x 0.${ftag} > log_x0${ftag}  2>&1&
done
