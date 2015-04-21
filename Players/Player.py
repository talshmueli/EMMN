__author__ = 'Tal'

class Player(object) :
    '''
    Abstract class for every kind of player
    '''
    def __init__(self, player_name) :
        self.__player_name = player_name

    def make_move(self, board):
        raise NotImplementedError()

    @property
    def player_name(self) :
        return self.__player_name