from Boards.Board import Board

__author__ = 'Tal'

import random
import math

class SplittingGameBoard1(Board):
    def __init__(self, h, dimension):
        self.__h = h
        self.__dimension = dimension
        self.__size = pow(2, (self.__h / 2))
        self.__board = self._make_board(dimension, self.__size)

    def __hash__(self):
        return hash(self.__board)

    def __eq__(self, obj) :
        return (isinstance(obj, SplittingGameBoard1) and obj.__board == self.__board)

    def __str__(self):
        if self.__dimension > 2 :
            return "Too many dimensions for display (%d)" % (self.__dimension,)
        return ''.join(["%s \n" % (i, ) for i in self.__board])

    def get_next_moves(self, player):
        dimension = player + 1
        # can choose one of the sides (in current dimension)
        return [(dimension, 0), (dimension, 1)]

    def make_move(self, dimension, side) :
        self.__board = self._split_board_by_dimension(self.__board,dimension, side)

    def is_game_over(self):
        if len(self.__board) != 1 :
            return False
        else :
            return self._is_game_over(self.__board)

    def _is_game_over(self, board):
        if isinstance(board, int) :
            return True
        elif len(board) == 1 and isinstance(board, tuple) :
            return self._is_game_over(board[0])
        elif len(board) == 1:
            return True
        else :
            return False

    def is_winner(self, player) :
        if not self._is_game_over(self.__board) :
            return False
        else :
            tmp = self.__board

            # reduce tuple
            while not isinstance(tmp, int) :
                tmp = tmp[0]


            return (tmp == player)

    def _get_random_raw(self, size):
        # return random raw where each cell contains some player's num
        return [random.randint(0, (self.__dimension-1)) for i in xrange(size)]

    def _make_board(self, dimension, size):
        if dimension == 1 :
            return tuple(self._get_random_raw(size))
        else :
            return tuple([self._make_board(dimension-1, size) for i in xrange(size)])

    def _split_board_by_dimension(self, board, dimension, side):
        if isinstance(board,int) :
            return board

        if dimension == 1:
            if side == 0 :
                return tuple(board[:len(board)/2])
            else :
                return tuple(board[len(board)/2:])
        else :
            return tuple([self._split_board_by_dimension(element, dimension-1, side) for element in board])

    def get_player_counter(self, player):
        if player > self.__dimension :
            raise ValueError("Got invalid player number")

        board_str = str(self.__board)
        return board_str.count(str(player))

    def get_total_cells(self):
        return int(math.pow(self.__size,self.__dimension))



