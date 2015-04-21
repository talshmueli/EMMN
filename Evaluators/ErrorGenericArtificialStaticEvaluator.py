__author__ = 'Tal'

from Evaluators.GenericArtificialStaticEvaluator import GenericArtificialStaticEvaluator

class ErrorGenericArtificialStaticEvaluator(GenericArtificialStaticEvaluator) :
    def __init__(self, players_num, error_rates, db_file_path = None) :
        super(ErrorGenericArtificialStaticEvaluator, self).__init__(players_num, error_rates, db_file_path)

    def evaluate(self, board, player):
        return super(ErrorGenericArtificialStaticEvaluator,self).evaluate(board, player), self.error_rates[player]

    def get_error_rates(self, board, player):
        return self.error_rates