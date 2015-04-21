__author__ = 'Tal'
from Evaluators.ArtificialStaticEvaluator import ArtificialStaticEvaluator

class ErrorArtificialStaticEvaluatorExtended(ArtificialStaticEvaluator) :
    def __init__(self, players_num, error_rate, db_file_path = None) :
        super(ErrorArtificialStaticEvaluatorExtended, self).__init__(players_num, error_rate, db_file_path)

    def evaluate(self, board, player):
        return super(ErrorArtificialStaticEvaluatorExtended,self).evaluate(board, player), self.error_rates

    def get_error_rates(self, board):
        return self.error_rates