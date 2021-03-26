mkdir -p Logfiles
mkdir -p Outfiles

#for i in $(seq 10 28); do
#    ftag="7${i}"
#    ./Analyze_Jadepixtxt.py  -i ../data/data_rs_0325_x0${ftag}.txt   -o Outfiles/test_0325_x0${ftag}.root -x 0.${ftag} > Logfiles/log_0325_x0${ftag}  2>&1&
#done
#
#
#for i in $(seq 0 9); do
#    ftag="70${i}"
#    ./Analyze_Jadepixtxt.py  -i ../data/data_rs_0325_x0${ftag}.txt   -o Outfiles/test_0325_x0${ftag}.root -x 0.${ftag} > Logfiles/log_0325_x0${ftag}  2>&1&
#done
#
#
#for i in $(seq 595 615); do
#    ./Analyze_Jadepixtxt.py  -i ../data/data_rs_0325_y5${i}.txt   -o Outfiles/test_rs_0325_y5${i}.root -y 5.${i} > Logfiles/log_0325_y5${i}  2>&1&
#done


# for i in $(seq 1800 100 4500); do
# #for i in 2950 3050 3150 3250 3350 ; do
# #for i in 2950 ; do
#     echo ${i}
#     ./Analyze_Jadepixtxt.py  -i ../data/data_rs_0326_tune50_z${i}.txt -o Outfiles/test_rs_0326_tune50_z${i}.root > Logfiles/log_rs_0326_rune50__z${i} 2>&1&
# done

#for i in $(seq 720 742); do
#    echo ${i}
#    #./Analyze_Jadepixtxt.py  -i ../data/data_rs_0326_tune94p1_x0${i}.txt -o Outfiles/test_rs_0326_tune94p1_x0${i}.root -x 0.${ftag} > Logfiles/log_rs_0326_rune94p1_x0${i} 2>&1&
#    ./Analyze_Jadepixtxt.py  -i ../data/data_rs_0326_tune94p1_x0${i}.txt -o Outfiles/test_rs_0326_tune94p1_x0${i}.root -x 0.${i} > Logfiles/log_rs_0326_rune94p1_x0${i} 2>&1&
#done
#
#
#for i in $(seq 608 623); do
#    echo ${i}
#    ./Analyze_Jadepixtxt.py  -i ../data/data_rs_0326_tune94p1_y5${i}.txt -o Outfiles/test_rs_0326_tune94p1_y5${i}.root -y 5.${i} > Logfiles/log_rs_0326_rune94p1_y5${i} 2>&1&
#done


# for i in $(seq 608 655); do
#     echo ${i}
#     ./Analyze_Jadepixtxt.py  -i ../data/data_rs_0326_tune94p2_y5${i}.txt -o Outfiles/test_rs_0326_tune94p2_y5${i}.root -y 5.${i} > Logfiles/log_rs_0326_rune94p2_y5${i} 2>&1&
# done

for i in $(seq 702 724); do
    echo ${i}
    ./Analyze_Jadepixtxt.py  -i ../data/archive/20210326/data_rs_0326_measure1_tune93p7_x0${i}.txt -o Outfiles/test_rs_0326_measure1_tune93p7_x0${i}.root -x 0.${i} > Logfiles/log_rs_0326_measure1_tune93p7_x0${i} 2>&1&
done

for i in $(seq 640 655); do
    echo ${i}
    ./Analyze_Jadepixtxt.py  -i ../data/archive/20210326/data_rs_0326_measure1_tune93p7_y5${i}.txt -o Outfiles/test_rs_0326_measure1_tune93p7_y5${i}.root -y 5.${i} > Logfiles/log_rs_0326_measure1_tune93p7_y5${i} 2>&1&
done
