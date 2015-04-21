__author__ = 'Tal'

from Evaluators.MaxNEvaluator import MaxNEvaluator
from Evaluators.Evaluator import Evaluator
from GenericArtificialStaticEvaluator import GenericArtificialStaticEvaluator


import random

class ArtificialStaticEvaluator(GenericArtificialStaticEvaluator) :
    def __init__(self, players_num, error_rate, db_file_path = None) :
        error_rates = [error_rate] * players_num
        super(ArtificialStaticEvaluator, self).__init__(players_num, error_rates, db_file_path)