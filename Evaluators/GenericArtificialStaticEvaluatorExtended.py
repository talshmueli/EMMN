__author__ = 'Tal'

from Evaluators.GenericArtificialStaticEvaluator import GenericArtificialStaticEvaluator

class ErrorGenericArtificialStaticEvaluatorExtended(GenericArtificialStaticEvaluator) :
    def __init__(self, players_num, error_rates, db_file_path = None) :
        super(ErrorGenericArtificialStaticEvaluatorExtended, self).__init__(players_num, error_rates, db_file_path)

    def evaluate(self, board, player):
        return super(ErrorGenericArtificialStaticEvaluatorExtended,self).evaluate(board, player), self.error_rates

    def get_error_rates(self, board):
        return self.error_rates