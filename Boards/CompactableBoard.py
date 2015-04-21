__author__ = 'Tal'

from Boards.Board import Board

class CompactableBoard(Board) :
    '''
    An abstract class for every board game that can be compacted
    '''

    def get_compact_version(self) :
        '''
        returns the compact version of the Board
        '''
        pass

    @staticmethod
    def get_boards_mapping(board, compact_board):
        '''
        return a mapping between heaps in a compact board to the board itself
        '''
        pass