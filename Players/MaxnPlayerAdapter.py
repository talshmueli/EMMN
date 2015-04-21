__author__  =  'Tal'

from Players.Player import Player
from Players.MaxnPlayer import MaxnPlayer
from Evaluators.MaxNEvaluator import MaxNEvaluator
from utils import LoggerManager
import copy

class MaxnPlayerAdapter(MaxnPlayer) :

    def __init__(self, player_num, player_name, depth, evaluator, players_num, parasite_players = [], endgame_db_path = None) :
        super(MaxnPlayerAdapter, self).__init__(player_num, player_name, depth, evaluator, players_num, endgame_db_path)
        self.__parasite_players = parasite_players
        self.__logger = LoggerManager.getLogger("main_log")

    def make_move(self, board, debug=True):
        # First let all parasite players to make a move and save it in their moves history

        self.__logger.debug("Now running parasite players :")

        # A list for moves to be calculated by MaxN soon
        prefix_moves = []

        for p in self.__parasite_players :
            self.__logger.info(p.player_name)
            # That action causes p to save that move to his moves history cache
            move = p.make_move(board, debug, prefix_moves)
            self.__logger.debug("Move taken %s" % (str(move),))
            prefix_moves.append(move)

        self.__logger.info(self.player_name)
        return MaxnPlayer.make_move(self, board, debug, prefix_moves)

    def get_parasite_moves_history(self):
        return self.__parasite_players_history
