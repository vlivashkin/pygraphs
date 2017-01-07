import unittest

from measure.distance import Distance
from measure.shortcuts import *
from tests import sample_graphs


class MeasureCommonTests(unittest.TestCase):
    def test_chain_all_distances_more_than_zero(self):
        start, end, n_params = 0.05, 0.5, 30
        for distance in Distance.get_all():
            for param in np.linspace(start, end, n_params):
                true_param = distance.scale.calc(sample_graphs.chain_graph, param)
                D = distance.getD(sample_graphs.chain_graph, true_param)
                for i in range(D.shape[0]):
                    for j in range(D.shape[1]):
                        self.assertTrue(D[i][j] >= 0,
                                        "{} < 0 at {}({}) {}, {}".format(D[i][j], distance.name, param, i, j))

    def test_chain_all_distances_symmetry_matrix(self):
        start, end, n_params = 0.005, 0.5, 30
        for distance in Distance.get_all():
            for param in np.linspace(start, end, n_params):
                true_param = distance.scale.calc(sample_graphs.chain_graph, param)
                D = distance.getD(sample_graphs.chain_graph, true_param)
                for i in range(D.shape[0]):
                    for j in range(i + 1, D.shape[1]):
                        self.assertTrue(sample_graphs.equal_double_strict(D[i][j], D[j][i]),
                                        "{} != {} at {}, {}".format(D[i][j], D[j][i], i, j))

    def test_chain_all_distances_main_diagonal_zero(self):
        start, end, n_params = 0.0001, 0.5, 30
        for distance in Distance.get_all():
            for param in np.linspace(start, end, n_params):
                true_param = distance.scale.calc(sample_graphs.chain_graph, param)
                D = distance.getD(sample_graphs.chain_graph, true_param)
                for i in range(D.shape[0]):
                    self.assertTrue(D[i][i] == 0)

    if __name__ == '__main__':
        unittest.main()
