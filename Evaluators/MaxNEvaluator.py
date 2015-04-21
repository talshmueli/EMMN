__author__ = 'Tal'

from Evaluators.Evaluator import Evaluator
import copy
import pickle
import consts
from createdb import read_endgame_db
from utils import MemCacheSingleton, LoggerManager
from Boards.CompactableBoard import CompactableBoard

MEM_CACHE_NAME = "MAXNEvaluatorCache"
ABSOLUTE_WIN_SCORE = 1
DB_FILE_PARSER_FUNC = read_endgame_db

class MaxNEvaluator(Evaluator) :
    def __init__(self, players_num, endgame_db_path = None):
        self.__players_num = players_num
        self.__endgame_db_path = endgame_db_path
        self.__mc = MemCacheSingleton.getMemCache(MEM_CACHE_NAME, self._maxn_search, endgame_db_path, DB_FILE_PARSER_FUNC)
        self.__logger = LoggerManager.getLogger("main_log")

    def __reduce__(self):
        return (self.__class__, (self.__players_num, self.__endgame_db_path))

    def evaluate(self, board, player):
        if isinstance(board, CompactableBoard) :
            b = board.get_compact_version()
            return self.__mc[(b, player)]

        return self.__mc[(board, player)]

    def _maxn_search(self, board, curr_player):
        if  board.is_game_over() :
            evaluation = [0] * self.__players_num
            if board.is_winner(curr_player) :
                evaluation[curr_player] = ABSOLUTE_WIN_SCORE
            return evaluation

        if self.__mc.has_key((board, curr_player)) :
            return self.__mc[(board, curr_player)]

        child_values = []
        moves = board.get_next_moves(curr_player)
        for move in moves  :
            b_copy = copy.deepcopy(board)
            b_copy.make_move(*move)
            next_player = (curr_player + 1) % self.__players_num

            #child_values.append(self._maxn_search(b_copy,  next_player))
            # Evaluate checks the db first and then calls this function again if necessary
            child_values.append(self.evaluate(b_copy,  next_player))

        curr_player_values = [child_values[i][curr_player] for i in xrange(len(child_values))]
        max_value = max(curr_player_values)
        max_index = curr_player_values.index(max_value)
        self.__mc[(board, curr_player)] = child_values[max_index]
        return child_values[max_index]

    def get_absolute_win_score(self) :
        return ABSOLUTE_WIN_SCORE

    def _load_endgame_db(self):
        '''
        loads a end game db into correct MemCache
        '''
        f = file(self.__endgame_db_path, "rb")
        counter = 0
        try :
            while True :
                board, player = pickle.load(f)
                maxn_value = pickle.load(f)
                self.__mc[(board,player)] = maxn_value
                counter += 1
        except EOFError :
            pass

        f.close()
        self.__logger.info("Number of records read from endgame db - %d" % (counter,))
