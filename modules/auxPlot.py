import matplotlib.pyplot as plt

## need to add parent directory to PYTHONPATH before importing 
import os, sys

## Habitado no habitado
def plot_occupation(df, experiment_dir):
    fig, ax = plt.subplots()
    num_houses = df['num_houses'].values
    df_num_empty_houses = df['num_empty_houses']/num_houses
    ax.plot(1 - df_num_empty_houses, label="Habitado")
    ax.plot(df_num_empty_houses, label="No habitado")
    ax.axhline(1, color='red', ls='--')
    ax.legend()
    fig.tight_layout()
    fig.savefig(experiment_dir + "/plots/" + "empty_house_balance.pdf")

def plot_household(fig, ax, experiment_dir, filename):
    ax.legend()
    fig.tight_layout()
    fig.savefig(experiment_dir + "/plots/" + filename)

def num_plot(ax, experiment_dir):
    fig = ax[0].get_figure()
    fig.tight_layout()
    fig.savefig(experiment_dir + "/plots/" + "number_stats.pdf")