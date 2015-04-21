__author__ = 'Tal'

from Evaluators.Evaluator import  Evaluator
from Boards.SplittingGameBoard1 import SplittingGameBoard1

class ErrorGenericSplittingGameBoardNaturalStaticEvaluator(Evaluator):
    def __init__(self, players_num):
        super(ErrorGenericSplittingGameBoardNaturalStaticEvaluator, self).__init__()
        self.__players_num = players_num

    def evaluate(self, board, player):
        assert isinstance(board, SplittingGameBoard1), "board is not SplittingGameBoard1"
        total_board_cells = board.get_total_cells()
        players_counters = [board.get_player_counter(i) for i in xrange(self.__players_num)]
        max_player = players_counters.index(max(players_counters))
        evaluation = [0] * self.__players_num
        evaluation[max_player] = 1
        error_rates = [(1 - float(players_counters[i])/total_board_cells) for i in xrange(self.__players_num)]
        return evaluation, error_rates

    def get_error_rates(self, board):
        assert isinstance(board, SplittingGameBoard1), "board is not SplittingGameBoard1"
        total_board_cells = board.get_total_cells()
        players_counters = [board.get_player_counter(i) for i in xrange(self.__players_num)]
        error_rates = [(1 - float(players_counters[i])/total_board_cells) for i in xrange(self.__players_num)]
        return error_rates
