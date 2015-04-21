__author__  =  'Tal'

from Players.Player import Player
from Boards.CompactableBoard import CompactableBoard
from utils import CustomizedProgressBar, MemCacheSingleton, LoggerManager, ProcessManager, apply_async, utils
import copy
import pickle
from createdb import read_endgame_db
import os
import errno


RUN_ASYNC = False
MEM_CACHE_NAME = "MAXNPlayerCache"
DB_FILE_PARSER_FUNC = read_endgame_db

class MaxnPlayer(Player) :
    def __init__(self, player_num, player_name, depth, evaluator, players_num, endgame_db_path = None) :
        super(MaxnPlayer, self).__init__(player_name)
        self.__player_num = player_num
        self.__depth = depth
        self.__evaluator = evaluator
        self.__players_num = players_num
        self.__moves_history = {}
        self.__endgame_db_path = endgame_db_path
        self.__mc = MemCacheSingleton.getMemCache(MEM_CACHE_NAME, self.maxn_search, endgame_db_path, DB_FILE_PARSER_FUNC)
        self.__logger = LoggerManager.getLogger("main_log")
        self.__process_manager = ProcessManager()
        self.__apply_async_func = apply_async

    def __reduce__(self):
        return (self.__class__, (self.__player_num, self.player_name, self.__depth, self.__evaluator, self.__players_num, self.__endgame_db_path))

    def make_move(self, board, debug=True, prefix_moves = []):
        try :
            child_values = []
            moves = board.get_next_moves(self.__player_num)
            moves_set = set(moves)
            prefix_moves_set = set(prefix_moves)
            prefix_moves_list = list(prefix_moves_set)
            other_moves_list = list(moves_set - prefix_moves_set)

            if debug :
                self.__logger.debug("Possible moves : %s" % (len(moves),))
            if self.__depth == 0 :
                raise Exception("Depth out of range (Maybe wasn't configured correct)")
            if not prefix_moves_set.issubset(moves_set) :
                raise Exception("Maxn Prefix moves must be a subset of the actual moves set")

            next_player = (self.__player_num + 1) % self.__players_num
            results = []

            # Event used for Pruning techniques
            event = ProcessManager.getEvent()
            
            for move in prefix_moves_list :
                b_copy = copy.deepcopy(board)
                b_copy.make_move(*move)
                if RUN_ASYNC :
                    results.append(self.__apply_async_func(self.maxn_search, (b_copy, self.__depth - 1 ,  next_player, event, False)))
                else :
                    results.append(self.maxn_search(b_copy, self.__depth-1, next_player, event, False))


            for move in other_moves_list :
                b_copy = copy.deepcopy(board)
                b_copy.make_move(*move)

                if RUN_ASYNC :
                    results.append(self.__apply_async_func(self.maxn_search, (b_copy, self.__depth - 1 ,  next_player, event, True)))
                else :
                    results.append(self.maxn_search(b_copy, self.__depth-1, next_player, event, True))

            p  = CustomizedProgressBar()
            self.__logger.debug("Now waiting for son processes results")
            for result in p(results) :
                if RUN_ASYNC :
                    r = result.get()
                else :
                    r = result
                # None result means it was stopped by a signaling event (Pruning)
                if r is not None :
                    child_values.append(r)

            if RUN_ASYNC and event.is_set() :
                self.__logger.debug("MaxN Immediate pruning has happend!")
                #child_values.append(self.maxn_search(b_copy, self.__depth - 1 ,  next_player ))

            curr_player_values = [child_values[i][self.__player_num] for i in xrange(len(child_values))]
            max_value = max(curr_player_values)
            max_indexes = utils.get_max_indexes(curr_player_values)
            #max_index = curr_player_values.index(max_value)

              # log and return next move
            self.__moves_history[copy.deepcopy(board)] = [moves[i] for i in max_indexes]
            #self.__moves_history[copy.deepcopy(board)] = moves[max_index]
            #return moves[max_index]
            return moves[max_indexes[0]]
            
        except IOError, e   :
            if e.errno == errno.EPIPE :
                print "PIPE ERROR"
                # Kill all sons and try again!
                event.set()
                return self.make_move(board, debug=True)
            else :
                raise e

    def maxn_search(self, board, depth, curr_player, event, allow_prune=True) :
        if board.is_game_over() or depth == 0 :
            return self.__evaluator.evaluate(board, curr_player)
        '''
        if isinstance(board, CompactableBoard) :
            # Compact the board if possible
            board = board.get_compact_version()
        '''

        if self.__mc.has_key((board, depth, curr_player)) :
            return self.__mc[(board, depth, curr_player)]

        child_values = []
        moves = board.get_next_moves(curr_player)
        for move in moves   :
            # If the event is set - this function which runs in some worker is not relevant anymore
            if RUN_ASYNC and (event is not None and event.is_set() and allow_prune) :
                break

            b_copy = copy.deepcopy(board)
            b_copy.make_move(*move)
            next_player = (curr_player + 1) % self.__players_num
            result = self.maxn_search(b_copy, depth - 1 , next_player, event)
            child_values.append(result)

        curr_player_values = [child_values[i][curr_player] for i in xrange(len(child_values)) if child_values[i] is not None]

        # If all sons returned None that means that all those subtrees were pruned
        
        if len(curr_player_values) == 0 :
            return None

        max_value = max(curr_player_values)
        max_index = curr_player_values.index(max_value)
        # Immediate Pruning
        if RUN_ASYNC and (event is not None and (max_value == self.__evaluator.get_absolute_win_score())) :
            self.__logger.debug("Got winning result, stopping all workers!")
            event.set()

        # store value and return it
        self.__mc[(board, depth, curr_player)] = child_values[max_index]
        return child_values[max_index]

    @property
    def player_num(self):
        return self.__player_num

    @property
    def depth(self):
        return self.__depth

    @property
    def evaluator(self):
        return self.__evaluator

    @property
    def players_num(self):
        return self.__players_num

    @property
    def moves_history(self):
        return self.__moves_history

    def get_moves_history(self):
        return self.__moves_history