__author__ = 'Tal'

from Evaluators.MaxNEvaluator import MaxNEvaluator
from Evaluators.Evaluator import Evaluator
import random

class GenericArtificialStaticEvaluator(Evaluator) :
    def __init__(self, players_num, error_rates, db_file_path = None) :
        if not isinstance(error_rates, list) :
            raise Exception("Should be a list of errors")
        elif len(error_rates) != players_num :
            raise Exception("No error rate for each player")

        self.__players_num = players_num
        self.__maxn_evaluator = MaxNEvaluator(players_num, db_file_path)
        self.__error_rates = error_rates

    def evaluate(self, board, player):

        evaluation = self.__maxn_evaluator.evaluate(board, player)
        new_evaluation = self.apply_mutation(evaluation)

        return new_evaluation
        '''
        if random.random() <= self.__error_rates[player] :
            real_winner = evaluation.index(max(evaluation))
            candidates = list(xrange(self.__players_num))
            candidates.remove(real_winner)
            evaluation = [0] * self.__players_num
            evaluation[self.choose_winner(candidates)] = 1
        '''
        return evaluation

    def apply_mutation(self, evaluation):
        new_evaluation = []
        for p in xrange(self.__players_num) :
            if random.random() <= self.__error_rates[p] :
                new_evaluation.append(1-evaluation[p])
            else :
                new_evaluation.append(evaluation[p])

        return new_evaluation

    # uniform selection of a random winner
    # Ideas :
    # 1) Maybe choose the winner according to the values in evaluation vector

    def choose_winner(self, candidates) :
        if 0 == len(candidates) :
            raise Exception("No candidates for a winner")

        return random.choice(candidates)

    @property
    def error_rates(self) :
        return self.__error_rates

