import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

plt.style.use('tableau-colorblind10')
plt.rcParams.update({'font.size': 12})

def simulate_daily_arrivals(df_acuity, df_arrival):
    '''Simulates the number of patients and each patients acuity level
       for each hour in the day.  Though number based on rate is
       normally associated with Poisson, the variance of the Poisson
       distribution is equal to the rate, and this data shows higher 
       than the convention Poisson.  Therefore the normal distribution 
       with the measured standard deviation will be used and discretized.'''
    data = [] 
    hours = df_arrival.index
    for hr in hours:
        rowdata = []
        mean = df_arrival.loc[hr, 'mean']
        std = df_arrival.loc[hr, 'std']
        patient_dist = stats.norm(loc=mean, scale=std)
        num_patients = patient_dist.rvs(1)[0]
        num_p = int(max(0, round(num_patients)))
        rowdata.append(num_p)
        # initialize counters for acuity levels
        na1, na2, na3, na4, na5, na6 = 0, 0, 0, 0, 0, 0
        acuity_dist = df_acuity.loc[hr, :].values
        for patient in range(num_p):
            acuity = np.random.choice([1, 2, 3, 4, 5, 6], p=acuity_dist)
            if acuity == 1:
                na1 += 1
            elif acuity == 2:
                na2 += 1
            elif acuity == 3:
                na3 += 1
            elif acuity == 4:
                na4 += 1
            elif acuity == 5:
                na5 += 1
            else:
                na6 += 1
        rowdata.extend([na1, na2, na3, na4, na5, na6])
        data.append(rowdata)
    cols = ['total_arrivals', 'arrivals_a1', 'arrivals_a2', 'arrivals_a3',
            'arrivals_a4', 'arrivals_a5', 'arrivals_a6']
    df_daily_arrivals = pd.DataFrame(data=data, columns=cols, index=hours)
    return df_daily_arrivals

def plot_daily_arrivals(df):
    cols = df.columns[1:]
    hours = df.index
    fig, ax = plt.subplots(figsize=(11,5))
    colors = [(0, 0.42, 0.64), (0.63, 0.78, 0.93), (0.67, 0.67, 0.67),
              (1, 0.74, 0.47), (1.00, 0.50, 0.05), (0.78, 0.12, 0)]
    df['0-a1'] = df['arrivals_a1']
    df['0-a2'] = df['0-a1'] + df['arrivals_a2']
    df['0-a3'] = df['0-a2'] + df['arrivals_a3'] 
    df['0-a4'] = df['0-a3'] + df['arrivals_a4'] 
    df['0-a5'] = df['0-a4'] + df['arrivals_a5'] 
    for i, col in enumerate(cols, 1):
        if col == 'arrivals_a1':
            ax.bar(hours, df[col], align='center', alpha=0.5, color=colors[i-1], 
                   label='Acuity '+str(i))
        else:
            ax.bar(hours, df[col], align='center', alpha=0.5, bottom=df['0-a'+str(i-1)],
                   color=colors[i-1], label = 'Acuity '+str(i))
    ax.set_xlabel('Hour of the Day')
    ax.set_ylabel('Number of Arriving Patients')
    ax.set_title('Number and Acuity of Level of Patients Arriving Each Hour in the Day')
    ax.set_xticks(hours)
    #ax.set_ylim([0, 1.05])
    ax.legend(bbox_to_anchor=(1.005, 0.5), loc='center left')
    plt.tight_layout()
    plt.savefig('./images/daily_arrival_simulation.png', dpi=150)
    plt.close()

if __name__ == '__main__':
    np.random.seed(42) 
    df_acuity = pd.read_csv('./data/acuity_distribution.csv', index_col=0)
    df_arrival = pd.read_csv('./data/patient_arrival_distribution.csv',
                             index_col=0)
    df_daily_arrivals = simulate_daily_arrivals(df_acuity, df_arrival)
    plot_daily_arrivals(df_daily_arrivals.copy())
