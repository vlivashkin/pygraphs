from _generated_kkmeans import generated_kkmeans
from _generated_kward import generated_kward
from _datasets_kkmeans import datasets_kkmeans
from part2 import calc_part2
from part3 import calc_part3
from part4 import calc_part4
from part5 import calc_part5
from part6 import calc_part6

if __name__ == '__main__':
    N_JOBS = 6

    print('### CALC CLASSIC GRAPHS KKMEANS ###')
    generated_kkmeans(n_jobs=N_JOBS)

    print('### CALC CLASSIC GRAPHS KWARD ###')
    generated_kward(n_jobs=N_JOBS)

    print('### CALC DATASETS KKMEANS ###')
    datasets_kkmeans(n_jobs=N_JOBS)

    print('### PART2 ###')
    calc_part2(n_jobs=N_JOBS)
    print('### PART3 ###')
    calc_part3(n_jobs=N_JOBS)
    print('### PART4 ###')
    calc_part4()
    print('### PART5 ###')
    calc_part5(n_jobs=N_JOBS)
    print('### PART6 ###')
    calc_part6(n_jobs=N_JOBS)
