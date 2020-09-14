import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

plt.style.use('tableau-colorblind10')
plt.rcParams.update({'font.size': 12})


def create_arrival_time_distributions(lst_fnames):
    d_arrivals = dict()
    acuity_names = []
    acuity_values = [] 
    for i, fname in enumerate(lst_fnames):
        name = fname.split('/')[-1].split('.')[0]
        vals = np.loadtxt(fname, delimiter=',')
        acuity_names.append(name)
        acuity_values.append(vals[:,1].copy())
        if i == 0:
            hours = vals[:,0].astype(int).copy()
    for i in range(len(acuity_names)):
        d_arrivals[acuity_names[i]] = acuity_values[i]
    return pd.DataFrame(data=d_arrivals, index=hours) 
        
def read_coefficient_of_variation(fname):
    d_cov = dict()
    vals = np.loadtxt(fname, delimiter=',')
    hours = vals[:,0].astype(int)
    cov = vals[:,1]
    d_cov['cov'] = cov
    return pd.DataFrame(data=d_cov, index=hours) 

def calculate_standard_deviation(means, covs):
    return means * covs

def plot_hourly_patient_arrival_distributions(hours, means, stds):
    fig, ax = plt.subplots(figsize=(10,5))
    ax.bar(hours, means, yerr=stds, align='center', ecolor='black', alpha=0.5)
    ax.set_xlabel('Hour of the Day')
    ax.set_ylabel('Average # of Patient Arrivals')
    ax.set_title('Average Emergency Department Hourly Patient Arrivals')
    ax.set_xticks(hours)
    ax.set_ylim([0, 16])
    plt.tight_layout()
    plt.savefig('./images/hourly_arrival_distribution.png', dpi=150)
    plt.close()

def create_hourly_acuity_level_distribution(df_arrival):
    df_adist = df_arrival.copy()
    cols = df_adist.columns.values
    for col in cols:
        if col == 'a1':
            df_adist['pa1'] = (df_adist['a1'] - 0)/df_adist['a6'] 
        else:
            df_adist['p' + col] = (df_adist[col] - df_adist[lastcol])/df_adist['a6'] 
        lastcol = col
    df_adist.drop(columns=cols, inplace=True)
    return df_adist

def create_cumsum_acuity_probability(df_adist):
    cumsum_lst = []
    nrows = df_adist.shape[0]
    for row in range(nrows):
       cumsum = df_adist.loc[row,:].cumsum()
       cumsum_lst.append(cumsum.values)
    cols = df_adist.columns
    df_adist_cumsum = pd.DataFrame(data=cumsum_lst, columns=cols)
    return df_adist_cumsum

def plot_hourly_acuity_level_distribution(hours, df_adist):
    cols = df_adist.columns.copy() 
    fig, ax = plt.subplots(figsize=(11,5))
    colors = [(0, 0.42, 0.64), (0.63, 0.78, 0.93), (0.67, 0.67, 0.67),
              (1, 0.74, 0.47), (1.00, 0.50, 0.05), (0.78, 0.32, 0)]
    df_adist['0-pa1'] = df_adist['pa1']
    df_adist['0-pa2'] = df_adist['pa1'] + df_adist['pa2']
    df_adist['0-pa3'] = df_adist['pa1'] + df_adist['pa2'] + df_adist['pa3'] 
    df_adist['0-pa4'] = df_adist['pa1'] + df_adist['pa2'] + df_adist['pa3'] + \
                       df_adist['pa4'] 
    df_adist['0-pa5'] = df_adist['pa1'] + df_adist['pa2'] + df_adist['pa3'] + \
                       df_adist['pa4'] + df_adist['pa5']
    for i, col in enumerate(cols, 1):
        if col == 'pa1':
            ax.bar(hours, df_adist['pa1'], align='center', alpha=0.5, color=colors[i-1], 
                   label='Acuity '+str(i))
        else:
            ax.bar(hours, df_adist[col], align='center', alpha=0.5, bottom=df_adist['0-'+lastcol],
                   color=colors[i-1], label = 'Acuity '+str(i))
        lastcol = col
    ax.set_xlabel('Hour of the Day')
    ax.set_ylabel('Acuity level proportion')
    ax.set_title('Hourly Acuity Level Distribution')
    ax.set_xticks(hours)
    ax.set_ylim([0, 1.05])
    ax.legend(bbox_to_anchor=(1.005, 0.5), loc='center left')
    plt.tight_layout()
    plt.savefig('./images/hourly_acuity_distribution.png', dpi=150)
    plt.close()


if __name__ == '__main__':
    arrival_filenames = ['./data/a1.csv', './data/a2.csv', './data/a3.csv', 
                         './data/a4.csv', './data/a5.csv', './data/a6.csv']
    df_arrival = create_arrival_time_distributions(arrival_filenames)
    df_cov = read_coefficient_of_variation('./data/a_cov.csv')
    stds = calculate_standard_deviation(df_arrival['a6'], df_cov['cov'])
    data = np.hstack([df_arrival['a6'].values.reshape(-1,1), 
                      stds.values.reshape(-1,1)])
    cols = ['mean', 'std']
    df_pdist = pd.DataFrame(data=data, columns=cols, index=stds.index)
    df_pdist = df_pdist.round(4)
    df_pdist.to_csv('./data/patient_arrival_distribution.csv')
    plot_hourly_patient_arrival_distributions(df_arrival.index, df_arrival['a6'], stds)
    df_adist = create_hourly_acuity_level_distribution(df_arrival)
    df_adist_cumsum = create_cumsum_acuity_probability(df_adist)
    df_adist = df_adist.round(4)
    df_adist.to_csv('./data/acuity_distribution.csv')
    df_adist_cumsum = df_adist_cumsum.round(4)
    df_adist_cumsum.to_csv('./data/acuity_distribution_cumsum.csv')
    plot_hourly_acuity_level_distribution(df_adist.index, df_adist.copy())






