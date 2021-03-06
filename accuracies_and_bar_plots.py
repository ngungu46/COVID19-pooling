import multiprocessing
import sys
import numpy as np
import time
import pickle
import matplotlib.pyplot as plt
from CoronaTestingSimulation import Corona_Simulation
from Statistics import Corona_Simulation_Statistics
import subprocess

'''
Accuracies and bar plot
Measure the sensitivities and false positives for the individual tests
'''

# default plot font sizes
SMALL_SIZE = 11
MEDIUM_SIZE = 14
BIGGER_SIZE = 16
plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


def getName(success_rate_test=0.99):
    # name for the data dump and plots
    name = 'accuracies'
    if success_rate_test != 0.99:
        name += '_{}'.format(success_rate_test)
    return name


def worker(return_dict, sample_size, prob_sick, success_rate_test, false_posivite_rate, test_strategy,
           num_simultaneous_tests, test_duration, group_size,
           tests_repetitions, test_result_decision_strategy, number_of_instances, scale_factor_pop):
    '''
    worker function for multiprocessing
    performs the same test tests_repetitions many times and returns expected valkues and standard deviations
    '''

    stat_test = Corona_Simulation_Statistics(prob_sick, success_rate_test,
                                             false_posivite_rate, test_strategy,
                                             num_simultaneous_tests, test_duration, group_size,
                                             tests_repetitions, test_result_decision_strategy, scale_factor_pop)

    stat_test.statistical_analysis(sample_size, num_simultaneous_tests, number_of_instances)
    print('Calculated {} for {} prob sick {}'.format(test_strategy, group_size, prob_sick))
    print('scaled to {} population and {} simulataneous tests\n'.format(sample_size, num_simultaneous_tests))
    # gather results
    worker_dict = {}
    worker_dict['e_num_tests'] = stat_test.e_number_of_tests
    worker_dict['e_time'] = stat_test.e_time
    worker_dict['e_num_confirmed_sick_individuals'] = stat_test.e_num_confirmed_sick_individuals
    worker_dict['e_false_positive_rate'] = stat_test.e_false_positive_rate
    worker_dict['e_ratio_of_sick_found'] = stat_test.e_ratio_of_sick_found
    worker_dict['e_number_sick_people'] = stat_test.e_number_sick_people
    worker_dict['e_num_sent_to_quarantine'] = stat_test.e_num_sent_to_quarantine
    worker_dict['sd_num_tests'] = stat_test.sd_number_of_tests
    worker_dict['sd_time'] = stat_test.sd_time
    worker_dict['sd_num_confirmed_sick_individuals'] = stat_test.sd_num_confirmed_sick_individuals
    worker_dict['sd_false_positive_rate'] = stat_test.sd_false_positive_rate
    worker_dict['sd_ratio_of_sick_found'] = stat_test.sd_ratio_of_sick_found
    worker_dict['sd_number_sick_people'] = stat_test.sd_number_sick_people
    worker_dict['sd_num_sent_to_quarantine'] = stat_test.sd_num_sent_to_quarantine

    return_dict['{}'.format(test_strategy)] = worker_dict


def calculation():
    start = time.time()
    randomseed = 19
    np.random.seed(randomseed)

    prob_sick = 0.05
    success_rate_test = 0.95
    false_posivite_rate = 0.01
    tests_repetitions = 1
    test_result_decision_strategy = 'max'
    if success_rate_test == 0.99:
        test_strategies = [
            ['individual-testing', 1],
            ['two-stage-testing', 5],
            ['binary-splitting', 8],
            ['purim', 10]
        ]
    elif success_rate_test == 0.95:
        test_strategies = [
            ['individual-testing', 1],
            ['two-stage-testing', 5],
            ['binary-splitting', 31],
            ['purim', 11]
        ]   
    elif success_rate_test == 0.9:
        test_strategies = [
            ['individual-testing', 1],
            ['two-stage-testing', 5],
            ['binary-splitting', 31],
            ['purim', 11]
        ]
    elif success_rate_test == 0.85:
        test_strategies = [
            ['individual-testing', 1],
            ['two-stage-testing', 5],
            ['binary-splitting', 32],
            ['purim', 11]
        ]
    elif success_rate_test == 0.75:
        test_strategies = [
            ['individual-testing', 1],
            ['two-stage-testing', 12],
            ['binary-splitting', 32],
            ['purim', 31]
        ]

    sample_size = 100000
    num_simultaneous_tests = 100
    number_of_instances = 10
    test_duration = 5
    scale_factor_pop = 100

    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    e_false_positive_rate = np.zeros((len(test_strategies)))
    e_ratio_of_sick_found = np.zeros((len(test_strategies)))
    e_num_confirmed_sick_individuals = np.zeros((len(test_strategies)))
    e_number_sick_people = np.zeros((len(test_strategies)))
    e_num_sent_to_quarantine = np.zeros((len(test_strategies)))

    sd_false_positive_rate = np.zeros((len(test_strategies)))
    sd_ratio_of_sick_found = np.zeros((len(test_strategies)))
    sd_num_confirmed_sick_individuals = np.zeros((len(test_strategies)))
    sd_number_sick_people = np.zeros((len(test_strategies)))
    sd_num_sent_to_quarantine = np.zeros((len(test_strategies)))

    jobs = []

    for i, (test_strategy, group_size) in enumerate(test_strategies):
        p = multiprocessing.Process(target=worker, args=(return_dict, sample_size, prob_sick,
                                                         success_rate_test, false_posivite_rate, test_strategy, num_simultaneous_tests,
                                                         test_duration, group_size, tests_repetitions, test_result_decision_strategy,
                                                         number_of_instances, scale_factor_pop))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()

    # gather results
    for i, (test_strategy, group_size) in enumerate(test_strategies):
        worker_dict = return_dict['{}'.format(test_strategy)]

        e_false_positive_rate[i] = worker_dict['e_false_positive_rate']
        e_ratio_of_sick_found[i] = worker_dict['e_ratio_of_sick_found']
        e_num_confirmed_sick_individuals[i] = worker_dict['e_num_confirmed_sick_individuals']
        e_number_sick_people[i] = worker_dict['e_number_sick_people']
        e_num_sent_to_quarantine[i] = worker_dict['e_num_sent_to_quarantine']

        sd_false_positive_rate[i] = worker_dict['sd_false_positive_rate']
        sd_ratio_of_sick_found[i] = worker_dict['sd_ratio_of_sick_found']
        sd_num_confirmed_sick_individuals[i] = worker_dict['sd_num_confirmed_sick_individuals']
        sd_number_sick_people[i] = worker_dict['sd_number_sick_people']
        sd_num_sent_to_quarantine[i] = worker_dict['sd_num_sent_to_quarantine']

    runtime = time.time()-start
    print('calculating took {}s'.format(runtime))
    # save data to allow plotting without doing the whole calculation again.
    data = {
        'randomseed': randomseed,
        'prob_sick': prob_sick,
        'success_rate_test': success_rate_test,
        'false_posivite_rate': false_posivite_rate,
        'tests_repetitions': tests_repetitions,
        'test_result_decision_strategy': test_result_decision_strategy,
        'test_strategies': test_strategies,
        'number_of_instances': number_of_instances,
        'test_duration': test_duration,
        'e_false_positive_rate': e_false_positive_rate,
        'e_ratio_of_sick_found': e_ratio_of_sick_found,
        'e_num_confirmed_sick_individuals': e_num_confirmed_sick_individuals,
        'e_number_sick_people': e_number_sick_people,
        'e_num_sent_to_quarantine': e_num_sent_to_quarantine,
        'sd_false_positive_rate': sd_false_positive_rate,
        'sd_ratio_of_sick_found': sd_ratio_of_sick_found,
        'sd_num_confirmed_sick_individuals': sd_num_confirmed_sick_individuals,
        'sd_number_sick_people': sd_number_sick_people,
        'sd_num_sent_to_quarantine': sd_num_sent_to_quarantine,
        'sample_size': sample_size,
        'runtime': runtime,
        'num_simultaneous_tests': num_simultaneous_tests,
    }
    filename = getName(success_rate_test)
    path = 'data/{}.pkl'.format(filename)
    with open(path, 'wb+') as fp:
        pickle.dump(data, fp)
    print('saved data as {}'.format(path))
    return filename


def plotting(filename, saveFig=0):
    # load data
    datapath = 'data/{}.pkl'.format(filename)
    with open(datapath, 'rb') as fp:
        data = pickle.load(fp)
    figpath = 'plots/{}'.format(filename)

    # extract relevant parameters from data
    success_rate_test = data['success_rate_test']
    test_strategies = data['test_strategies']
    e_ratio_of_sick_found = data['e_ratio_of_sick_found']
    e_false_positive_rate = data['e_false_positive_rate']
    e_num_confirmed_sick_individuals = data['e_num_confirmed_sick_individuals']
    e_num_sent_to_quarantine = data['e_num_sent_to_quarantine']
    sd_ratio_of_sick_found = data['sd_ratio_of_sick_found']
    sd_false_positive_rate = data['sd_false_positive_rate']
    # e_number_groupwise_tests = data['e_number_groupwise_tests']

    # plotting
    colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']

    ######## poolsize / expected time ########
    plt.figure(figsize=(6, 4))
    ax = plt.subplot(1, 2, 1)
    for i, (test_strategy, group_size) in enumerate(test_strategies):
        plt.errorbar([i], e_ratio_of_sick_found[i], sd_ratio_of_sick_found[i], label=test_strategy,
                     capsize=10, linestyle='None', linewidth=10, color=colors[i])
        plt.errorbar([i], e_ratio_of_sick_found[i], 0, capsize=5, linestyle='None', linewidth=10, color='k')
    plt.ylabel('sensitivity')
    plt.xticks(range(len(test_strategies)), ['ind.', '2l-p.', 'bin.', 'r.bin.', 'pu.', 's-r1'])
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.xlim([-0.5, len(test_strategies)])

    ax = plt.subplot(1, 2, 2)
    for i, (test_strategy, group_size) in enumerate(test_strategies):
        plt.errorbar([i], e_false_positive_rate[i], sd_false_positive_rate[i], label=test_strategy,
                     capsize=10, linestyle='None', linewidth=10, color=colors[i])
        plt.errorbar([i], e_false_positive_rate[i], 0, capsize=5, linestyle='None', linewidth=10, color='k')
    plt.ylabel('expected false positive rate')
    plt.xticks(range(len(test_strategies)), ['ind.', '2l-p.', 'bin.', 'r.bin.', 'pu.', 's-r1'])
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.xlim([-0.5, len(test_strategies)])

    plt.tight_layout(pad=1.0)
    if saveFig:
        plt.savefig(figpath+'.pdf', bbox_inches='tight')

    ######## test per 1M / bar plot - infected/identified/sent to quarantine ########
    labels = ['ind.', '2l-p.', 'bin.', 'r.bin.', 'pu.', 's-r1']

    if success_rate_test == 0.99:
        labelheight = 150
    elif success_rate_test == 0.95:
        labelheight = 200
    elif success_rate_test == 0.75:
        labelheight = 1050
    if success_rate_test == 0.99:
        numberheight = 70
    elif success_rate_test == 0.95:
        numberheight = 60
    elif success_rate_test == 0.9:
        numberheight = 50
    elif success_rate_test == 0.75:
        numberheight = 20

    X = np.arange(len(labels))  # the label locations
    plt.figure(figsize=(6, 5))
    width = 0.3  # the width of the bars

    fig, ax = plt.subplots()
    for i, _ in enumerate(test_strategies):
        ax.bar(X[i] - width/2, e_num_confirmed_sick_individuals[i], width,
               label='correctly identified infected', color=colors[i], edgecolor='black')
        ax.annotate('{}'.format(int(e_num_confirmed_sick_individuals[i])),
                    xy=(X[i] - 6*width / 8, e_num_confirmed_sick_individuals[i]+numberheight),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points", ha='center', va='bottom')

        ax.bar(X[i] + width/2, e_num_sent_to_quarantine[i], width,
               label='sent to quarantine', color=colors[i], alpha=0.6, edgecolor='black')
        ax.annotate('{}'.format(int(e_num_sent_to_quarantine[i])),
                    xy=(X[i] + 6*width / 8, e_num_sent_to_quarantine[i]+numberheight),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points", ha='center', va='bottom')

        ax.text(X[i]-width/2-width/4, labelheight, 'correctly identified', rotation=90)
        ax.text(X[i]+width/2-width/4, labelheight, 'total quarantined', rotation=90)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('number of individuals')
    ax.set_xticks(X)
    ax.set_xticklabels(labels[:len(test_strategies)])
    plt.xlim([-1.5, len(test_strategies)])
    plt.plot([-1.5, len(test_strategies)], [1000, 1000], '--k')
    plt.text(-1.45, 1030, 'infected')
    plt.text(-1.45, 900, 'individuals')

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    if saveFig:
        plt.savefig(figpath+'_bar.pdf', bbox_inches='tight')


if __name__ == "__main__":
    # either do calculations
    #filename = calculation()

    # or use precalculated data
    filename = getName(success_rate_test=0.95)

    saveFig = 0
    plotting(filename, saveFig)
    if saveFig == 0:
        plt.show()