import pandas as pd
import numpy as np
import scipy as sp
import glob
import os
from omegaconf import OmegaConf

import matplotlib.pyplot as plt
import pathlib
from matplotlib import cm
plt.style.use('bmh')
import seaborn as sns

plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 8
plt.rcParams['legend.fontsize'] = 7
plt.rcParams['legend.loc'] = 'lower right'
plt.rcParams['figure.facecolor'] = '#FFFFFF'

files = [
'/home/hossein/RL/effective_drq/drq/cheetah_run_old/165919__cheetah_run_eval2k_effective_True_seed_10/eval.csv',
'/home/hossein/RL/effective_drq/drq/cheetah_run_old/125559__cheetah_run_eval2k_effective_True_seed_7/eval.csv',
'/home/hossein/RL/effective_drq/drq/cheetah_run_old/175004__cheetah_run_eval2k_effective_True_seed_2/eval.csv',
'/home/hossein/RL/effective_drq/drq/cheetah_run_old/212640__cheetah_run_eval2k_effective_True_seed_6/eval.csv'
]



nrow = 1
ncol = 1

fig, axs = plt.subplots(nrow, ncol, figsize=(4 * ncol, 3 * nrow))
whole_data = pd.DataFrame()
for file in files:

    df = pd.read_csv(file)
    df['true_step'] = df['episode'] / 1000.
    data = df
    data = data[data['episode'] <= 2000]
    whole_data = whole_data.append(data)


row = 0 // ncol
col = 0 % ncol
ax = axs
sns.lineplot(x='true_step', y='episode_reward', data=whole_data, ci='sd', ax=ax)
ax.set_xlabel('Environment Steps ($\\times 10^6%$)')
ax.set_ylabel('Episode Return')
ax.set_title('Cheetah Run')

plt.tight_layout()
plt.show()
