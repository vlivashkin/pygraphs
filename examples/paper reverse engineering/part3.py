import os
import sys
import warnings

os.environ["OPENBLAS_NUM_THREADS"] = "1"
warnings.filterwarnings("ignore")
sys.path.append('../..')

from collections import defaultdict
from itertools import product
import numpy as np
from tqdm import tqdm
from sklearn.metrics import adjusted_rand_score
from scipy import stats

from pygraphs.graphs.generator import StochasticBlockModel
from pygraphs.measure import kernels
from pygraphs.cluster import KKMeans_iterative as KKMeans
from pygraphs.scenario import ParallelByGraphs
from pygraphs.scorer import copeland
from pygraphs.util import load_or_calc_and_save, ddict2dict


@load_or_calc_and_save('cache/3_best_params_3_100_ward.pkl')
def _calc_best_params(n_graphs=100, n_jobs=-1):
    """find best params and 95% percentile"""

    # calc data to find best params
    results = defaultdict(lambda: defaultdict(lambda: 0))
    for column in tqdm(list(product([100, 200], [2, 4], [0.1, 0.15]))):
        n_nodes, n_classes, p_out = column
        graphs, info = StochasticBlockModel(n_nodes, n_classes, p_in=0.3, p_out=p_out).generate_graphs(n_graphs)
        classic_plot = ParallelByGraphs(adjusted_rand_score, np.linspace(0, 1, 31), progressbar=False)
        for measure_class in tqdm(kernels, desc=str(column)):
            results[column][measure_class.name] = classic_plot.perform(KKMeans, measure_class, graphs, n_classes,
                                                                       n_jobs=n_jobs)

    # find best params
    best_params = defaultdict(lambda: defaultdict(lambda: 0))
    percentile_params = defaultdict(lambda: defaultdict(lambda: 0))
    for column, measures in results.items():
        for measure_name, measure_results in measures.items():
            x, y, error = measure_results
            best_idx = np.argmax(y)
            percentile_idx = list(y).index(np.percentile(y, 90, interpolation='lower'))
            print(f'{column}\t{measure_name.ljust(8, " ")}\t'
                  f'{x[best_idx]:0.2f} ({y[best_idx]:0.2f})\t{x[percentile_idx]:0.2f} ({y[percentile_idx]:0.2f})')
            best_params[column][measure_name] = x[best_idx]
            percentile_params[column][measure_name] = x[percentile_idx]
    return ddict2dict(best_params), ddict2dict(percentile_params)


def _calc_competitions(best_params, n_graphs=600):
    """calc competition for given params"""
    results = defaultdict(lambda: defaultdict(lambda: 0))
    for column in tqdm(list(product([100, 200], [2, 4], [0.1, 0.15]))):
        n_nodes, n_classes, p_out = column
        graphs, info = StochasticBlockModel(n_nodes, n_classes, p_in=0.3, p_out=p_out).generate_graphs(n_graphs)
        success = 0
        for edges, nodes in tqdm(graphs, desc=str(column)):
            try:
                single_competition_best = {}
                for kernel_class in kernels:
                    best_param = best_params[column][kernel_class.name]
                    kernel = kernel_class(edges)
                    param = kernel.scaler.scale(best_param)
                    K = kernel.get_K(param)
                    y_pred = KKMeans(n_classes).fit_predict(K)
                    ari = adjusted_rand_score(nodes, y_pred)
                    single_competition_best[kernel_class.name] = ari
                single_competition_score = copeland(single_competition_best.items())
                for measure_name, delta in single_competition_score.items():
                    results[column][measure_name] += delta
                    results['sum'][measure_name] += delta
                success += 1
            except Exception or FloatingPointError as e:
                print(e)
            if success == 200:
                break
    return results


def _print_results(results):
    mr_transposed = {}
    for column_name, column_results in results.items():
        mr_transposed[str(column_name)] = stats.rankdata([-column_results[x.name] for x in kernels], 'min')

    columns_right_order = [
        '(100, 2, 0.1)',
        '(100, 2, 0.15)',
        '(100, 4, 0.1)',
        '(100, 4, 0.15)',
        '(200, 2, 0.1)',
        '(200, 2, 0.15)',
        '(200, 4, 0.1)',
        '(200, 4, 0.15)',
        'sum'
    ]

    print('\t'.join(columns_right_order))
    for idx, kernel in enumerate(kernels):
        print(kernel.name, '\t', '\t'.join([str(mr_transposed[col_name][idx]) for col_name in columns_right_order]))


def calc_part3(n_graphs_train=100, n_graphs_inference=600, n_jobs=6):
    best_params, percentile_params = _calc_best_params(n_graphs=n_graphs_train, n_jobs=n_jobs)

    for setup in best_params.keys():
        print(setup, end='\t')
    print()
    for kernel in kernels:
        print(kernel.name, end='\t')
        for setup in best_params.keys():
            print(f"{best_params[setup][kernel.name]:.2f}", end='\t')
        print()

    # best
    results = _calc_competitions(best_params, n_graphs=n_graphs_inference)

    for column_name, column_results in results.items():
        print(column_name, [(x.name, column_results[x.name]) for x in kernels])

    _print_results(results)

    # percentile
    results = _calc_competitions(percentile_params, n_graphs=n_graphs_inference)

    for column_name, column_results in results.items():
        print(column_name, [(x.name, column_results[x.name]) for x in kernels])

    _print_results(results)


if __name__ == '__main__':
    calc_part3()
