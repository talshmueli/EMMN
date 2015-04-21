__author__ = 'Tal'
from Evaluators.ArtificialStaticEvaluator import ArtificialStaticEvaluator

class ErrorArtificialStaticEvaluator(ArtificialStaticEvaluator) :
    def __init__(self, players_num, error_rate, db_file_path = None) :
        super(ErrorArtificialStaticEvaluator, self).__init__(players_num, error_rate, db_file_path)

    def evaluate(self, board, player):
        return super(ErrorArtificialStaticEvaluator,self).evaluate(board, player), self.error_rates[player]

