__author__ = 'Tal'


class Board (object):
    '''
    An abstract class for every board game
    '''

    def __hash__(self):
        raise NotImplementedError()

    def __eq__(self, obj) :
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    def is_winner(self, player):
        raise NotImplementedError()

    def get_next_moves(self, player):
        raise NotImplementedError()

    def make_move(self, heap, numOfObjects) :
        raise NotImplementedError()

    def is_game_over(self):
        raise NotImplementedError()


