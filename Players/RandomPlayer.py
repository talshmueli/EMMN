__author__ = 'Tal'

from Players.Player import Player
import random
import copy

class RandomPlayer(Player) :
    def __init__(self, player_num, player_name,  depth, evaluator, players_num) :
        super(RandomPlayer, self).__init__(player_name)
        self.__player_num = player_num
        self.__depth = depth
        self. __evaluator = evaluator
        self.__players_num = players_num
        self.__moves_history = {}

    def make_move(self, board):
        moves = board.get_next_moves(self.__player_num)
        print "Possible moves : %s" % (len(moves),)
        move = random.choice(moves)
        self.__moves_history[copy.deepcopy(board)] = move

        return move

    def get_moves_history(self):
        return self.__moves_history


