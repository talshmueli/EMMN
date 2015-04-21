
from Boards.CompactableBoard import CompactableBoard

__author__ = 'Tal'

import random
import itertools
import math

WINNER_RETURN_VALUE = True

def boardgen(product_iter) :
    '''
    Implements generator that wrappes/objectize an iterator of board
    '''
    while True :
        yield NimBoard(None, None, None, list(next(product_iter)))

class NimBoard(CompactableBoard):

    def __init__(self, numOfHeaps, lowerBound, upperBound, heaps = []) :
        self.__numOfHeaps = numOfHeaps
        self.__lowerBound = lowerBound
        self.__upperBound = upperBound

        if [] != heaps :
            self.__heaps = heaps
            self.__numOfHeaps = len(heaps)
        else :
            self.__heaps = [random.randint(lowerBound, upperBound) for i in xrange(numOfHeaps)]
    def __hash__(self):
        return hash(str(self.__heaps))
    def __eq__(self, obj) :
        return (isinstance(obj, NimBoard) and obj.__heaps == self.__heaps)
    def __str__(self):
        return "".join( ["[%s]  %s\n" %  (str(i), "#" * self.__heaps[i]) for i in xrange(self.__numOfHeaps)])

    @property
    def heaps(self):
        return self.__heaps

    def get_next_moves(self, player):
        next_moves =  [list(itertools.product([idx], range(1,heap+1))) for (idx,heap) in enumerate(self.__heaps)]
        return reduce(lambda x,y : x+y, next_moves)

    def make_move(self, heap, numOfObjects) :
        if len(self.__heaps) < heap :
            raise IndexError()

        if self.__heaps[heap] < numOfObjects :
            self.__heaps[heap] = 0
        else :
            self.__heaps[heap] -= numOfObjects

        return self.is_game_over()

    def is_game_over(self):
            if sum(self.__heaps) == 0 :
                return True
            else :
                return False

    def get_binary_rep(self):
        '''
        returns the binary rep of the board (heaps)
        '''
        rep_max_size = int(math.ceil(math.log(max(self.__heaps) + 1, 2)))
        return [bin(h)[2:].zfill(rep_max_size) for h in self.__heaps]

    def get_nim_sum(self):
        nim_sum = ''
        binary_rep = self.get_binary_rep()
        rep_max_size = int(math.ceil(math.log(max(self.__heaps) + 1, 2)))
        for s in xrange(rep_max_size) :
            nim_sum += str(sum([int(b[s]) for b in binary_rep]) % 2)

        return nim_sum

    def get_compact_version(self) :
        # Return the compact version (no empty columns)
        heaps = [i for i in self.__heaps if i is not 0]

        # If it's a endgame state, return the compact version of it
        if [] == heaps :
            heaps = [0]

        return NimBoard(None, None, None, heaps)

    def is_winner(self, player):
        return self.is_game_over()

    @staticmethod
    def get_boards_mapping(board, compact_board):
        '''
        return a mapping between heaps in a compact board to the board itself
        '''
        expected_compact = [i for i in board.heaps if i is not 0]
        if not expected_compact == compact_board.heaps :
            raise ValueError("Not the correct compact version!")

        mapping = {}
        for idx, heapx in enumerate(compact_board.heaps) :
            for idy, heapy in enumerate(board.heaps) :
                if heapx == heapy :
                    mapping[idx] = idy

        return mapping


    @staticmethod
    def generate_boards_generator(numOfHeaps, lowerBound, upperBound):

        # Create a list of lists for cartesian product calculation
        l = range(lowerBound, (upperBound + 1))
        lists = [l for i in xrange(numOfHeaps)]
        boards_iter = itertools.product(*lists)
        return boardgen(boards_iter)
