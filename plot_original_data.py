# I added it to get a plot of data/dmc_dreamer_bench.csv

import pandas as pd
from logger import Logger
import os


def main(file_address, env, action_repeat, run_id):
    log_file = pd.read_csv(file_address)
    work_dir = os.getcwd()
    logger = Logger(work_dir + "/" + env + "/" + "_runid_" + str(run_id)+"_seed_"+str(run_id+1), True,
                    action_repeat=action_repeat)

    for index, row in log_file.iterrows():
        if row['env'] == env:
            if int(row['run_id'][4:]) == 20+run_id:
                logger.log('eval/episode_reward', float(row['episode_reward']), -1 * int(row['step']))
                # if  int(row['episode'])>550:
                #     break

if __name__ == '__main__':
    file_address = "data/dmc_planet_bench.csv"
    env = 'cheetah_run'
    action_repeat = 4
    for run_id in range(10):
        main(file_address, env, action_repeat, run_id)
