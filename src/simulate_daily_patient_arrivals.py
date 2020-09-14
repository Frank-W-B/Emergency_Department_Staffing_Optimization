import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

plt.style.use('tableau-colorblind10')
plt.rcParams.update({'font.size': 12})

def simulate_daily_arrivals(df_acuity, df_arrival):
    '''Simulates the number of patients and each patient's acuity level
       for each hour in the day.  Though a discreted number based on a rate is
       usually associated with the Poisson distribution, the variance of the 
       Poisson distribution is equal to the rate, and this data shows higher 
       variance than the conventional Poisson.  Therefore the normal distribution 
       with the measured standard deviation will be used and discretized.'''
    data = [] 
    hours = df_arrival.index
    for hr in hours:
        rowdata = []
        mean = df_arrival.loc[hr, 'mean']
        std = df_arrival.loc[hr, 'std']
        patient_dist = stats.norm(loc=mean, scale=std)
        num_patients = patient_dist.rvs(1)[0]
        num_p = int(max(0, round(num_patients))) # 0 to some integer value
        rowdata.append(num_p)
        # initialize acuity level counter
        acuity_counts = [0, 0, 0, 0, 0, 0] # acuity level 1 - acuity level 6 
        acuity_dist = df_acuity.loc[hr, :].values
        for _ in range(num_p):
            acuity = np.random.choice([1, 2, 3, 4, 5, 6], p=acuity_dist)
            acuity_counts[acuity - 1] += 1
        rowdata.extend(acuity_counts)
        data.append(rowdata)
    cols = ['total_arrivals', 'arrivals_a1', 'arrivals_a2', 'arrivals_a3',
            'arrivals_a4', 'arrivals_a5', 'arrivals_a6']
    df_daily_arrivals = pd.DataFrame(data=data, columns=cols, index=hours)
    return df_daily_arrivals

def stack_columns(df):
    '''Required to make stacked bar plot in matplotlib'''
    df['0-a1'] = df['arrivals_a1']
    df['0-a2'] = df['0-a1'] + df['arrivals_a2']
    df['0-a3'] = df['0-a2'] + df['arrivals_a3'] 
    df['0-a4'] = df['0-a3'] + df['arrivals_a4'] 
    df['0-a5'] = df['0-a4'] + df['arrivals_a5'] 

def plot_daily_arrivals(df, colors, fname):
    cols = df.columns[1:]
    hours = df.index
    fig, ax = plt.subplots(figsize=(11,5))
    stack_columns(df)
    for i, col in enumerate(cols, 1):
        if col == 'arrivals_a1':
            ax.bar(hours, df[col], align='center', alpha=0.5, color=colors[i-1], 
                   label='Acuity '+str(i))
        else:
            ax.bar(hours, df[col], align='center', alpha=0.5, bottom=df['0-a'+str(i-1)],
                   color=colors[i-1], label = 'Acuity '+str(i))
    ax.set_xlabel('Hour of the Day')
    ax.set_ylabel('Number of Arriving Patients')
    ax.set_title('Number and Acuity Level of Patients Arriving Each Hour in the Day')
    ax.set_xticks(hours)
    ax.set_ylim([0, 24])
    ax.set_yticks(np.arange(0, 26, 2))
    ax.legend(bbox_to_anchor=(1.005, 0.5), loc='center left')
    plt.tight_layout()
    plt.savefig('./images/' + fname, dpi=150)
    plt.close()

def plot_several_days(day_lst, colors, fname):
    ndays = len(day_lst) 
    day0 = day_lst[0]
    cols = day0.columns[1:]
    hours = day0.index
    figheight = 2 * ndays 
    fig, axs = plt.subplots(nrows=ndays, ncols=1, figsize=(11,figheight))
    for i, day in enumerate(day_lst):
        stack_columns(day)
        for j, col in enumerate(cols, 1):
            if col == 'arrivals_a1':
                axs[i].bar(hours, day[col], align='center', alpha=0.5, color=colors[j-1], 
                           label='Acuity '+str(j))
            else:
                axs[i].bar(hours, day[col], align='center', alpha=0.5, bottom=day['0-a'+str(j-1)],
                           color=colors[j-1], label = 'Acuity '+str(j))
        axs[i].set_xticks(hours)
        axs[i].set_ylim([0, 24])
        axs[i].set_yticks(np.arange(0, 26, 4))
        if i == 0:
            axs[i].set_title(f'Simulating {ndays} days of patient arrivals', fontsize=18)
        if i == ndays - 1:
            axs[i].set_xlabel('Hour of the day', fontsize=16)
        if i == ndays // 2:
            axs[i].set_ylabel('# Arrivals', fontsize=16)
            axs[i].legend(bbox_to_anchor=(1.005, 0.5), loc='center left')
    plt.tight_layout()
    plt.savefig('./images/' + fname, dpi=150)
    plt.close()


if __name__ == '__main__':
    np.random.seed(42) 
    # colors for acuity levels, a1-a6 
    colors = [(0, 0.42, 0.64), (0.63, 0.78, 0.93), (0.67, 0.67, 0.67),
              (1, 0.74, 0.47), (1.00, 0.50, 0.05), (0.78, 0.12, 0)]
    
    # required acuity and arrival distributions 
    df_acuity = pd.read_csv('./data/acuity_distribution.csv', index_col=0)
    df_arrival = pd.read_csv('./data/patient_arrival_distribution.csv',
                             index_col=0)
    # simulate one day 
    df_daily_arrivals = simulate_daily_arrivals(df_acuity, df_arrival)
    plot_daily_arrivals(df_daily_arrivals.copy(), colors, 'single-day_arrival_simulation.png')

    # perform multiday simulation
    n_sim = 5 # number of days
    days = [simulate_daily_arrivals(df_acuity, df_arrival) for _ in range(n_sim)]
    plot_several_days(days, colors, 'multi-day_arrival_simulation.png')

