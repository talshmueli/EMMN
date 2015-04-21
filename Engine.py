__author__ = 'Tal'

from utils import LoggerManager

class Engine(object) :
    def __init__(self, board, players):
        self.__current_player = 0
        self.__board = board
        self.__players = players
        self.__logger = LoggerManager.getLogger("main_log")

    def run_game(self):
        curr_player = 0
        while not self.__board.is_game_over() :
            self.__logger.info("%s's turn :" % (self.__players[curr_player].player_name))
            move = self.__players[curr_player].make_move(self.__board)
            self.__board.make_move(*move)
            curr_player  = (curr_player + 1) % len(self.__players)
            self.__logger.debug("Move taken %s" % (str(move),))
            self.__logger.info("Current board:\n%s" % (str(self.__board),))

        return curr_player