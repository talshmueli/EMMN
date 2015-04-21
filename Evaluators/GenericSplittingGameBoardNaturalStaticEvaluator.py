__author__ = 'Tal'

from Evaluators.Evaluator import  Evaluator
from Boards.SplittingGameBoard1 import SplittingGameBoard1

class GenericSplittingGameBoardNaturalStaticEvaluator(Evaluator):
    def __init__(self, players_num):
        super(GenericSplittingGameBoardNaturalStaticEvaluator, self).__init__()
        self.__players_num = players_num

    def evaluate(self, board, player):
        assert isinstance(board, SplittingGameBoard1), "board is not SplittingGameBoard1"
        players_counters = [board.get_player_counter(i) for i in xrange(self.__players_num)]
        max_player = players_counters.index(max(players_counters))
        evaluation = [0] * self.__players_num
        evaluation[max_player] = 1
        return evaluation