__author__ = 'Tal'

import copy
from Players.Player import Player
from utils import utils, CustomizedProgressBar, LoggerManager, ProcessManager, apply_async
import pickle

RUN_ASYNC = False

class EMMNPlayer(Player) :
    def __init__(self, player_num, player_name, depth, evaluator, players_num) :
        super(EMMNPlayer, self).__init__(player_name)
        self.__player_num = player_num
        self.__depth = depth
        self.__evaluator = evaluator
        self.__players_num = players_num
        self.__moves_history = {}
        self.__logger = LoggerManager.getLogger("main_log")
        self.__apply_async_func = apply_async

    def __reduce__(self):
        return (self.__class__, (self.__player_num, self.player_name, self.__depth, self.__evaluator, self.__players_num))

    def make_move(self, board,debug = True, prefix_moves = []):
    
        # Not implemented yet
        if len(prefix_moves) != 0 :
            self.__logger.debug("Warning :: prefix_moves beavior for EMMN_PLAYER is not implemented")
            
        child_values_errors = []
        moves = board.get_next_moves(self.__player_num)
        #widgets = [FormatLabel(''), ' ', Percentage(), ' ', Bar('/'), ' ', RotatingMarker()]
        p  = CustomizedProgressBar()
        self.__logger.info("Possible moves : %s" % (len(moves),))

        results = []
        for move in p(moves) :
            b_copy = copy.deepcopy(board)
            b_copy.make_move(*move)
            next_player = (self.__player_num + 1) % self.__players_num
            parameters = (b_copy, self.__depth - 1 , next_player)
            if RUN_ASYNC :
                results.append(self.__apply_async_func(self.emmn_search, parameters))
            else :
                results.append(self.emmn_search(*parameters))

        p  = CustomizedProgressBar()
        self.__logger.debug("Now waiting for son processes results")
        for result in p(results) :

            if RUN_ASYNC :
                val, err = result.get()
            else :
                val, err = result
            #val, err = self.emmn_search(b_copy, self.__depth - 1 , next_player)
            child_values_errors.append({"val" : val, "err" : err})

        # Achieve max value for current player with minimum error value
        curr_player_values = [child_values_errors[i]["val"][self.__player_num] for i in xrange(len(child_values_errors))]
        max_value = max(curr_player_values)
        max_values_errors_set = [(child_values_errors[i]["err"],i) for i in xrange(len(curr_player_values)) if curr_player_values[i] == max_value]

        min_error, max_value_min_error_index = min(max_values_errors_set)

        # Log move and return
        self.__moves_history[copy.deepcopy(board)] = moves[max_value_min_error_index]
        return moves[max_value_min_error_index]

    def emmn_search(self, board, depth, curr_player) :
        children_values_errors = []

        # if the game is over or we reached the limited depth,
        # then we return the evaluation function value on that node
        # note to myself - it's ok that depth is also here!
        if board.is_game_over() or depth == 0 :
            return self.__evaluator.evaluate(board, curr_player)

        # determine children values and aggErrs
        moves =  board.get_next_moves(curr_player)
        for move in moves :
            #print "Possible moves : %s" % (len(moves),)
            b_copy = copy.deepcopy(board)
            b_copy.make_move(*move)
            next_player = (curr_player + 1) % self.__players_num
            val, err = self.emmn_search(b_copy, depth - 1 , next_player)
            children_values_errors.append({"val" : val, "err" : err})

        curr_player_values = [children_values_errors[i]["val"][curr_player] for i in xrange(len(children_values_errors))]
        max_value = max(curr_player_values)
        # Todo - check wether we should choose the minimum error from a set of errors
        max_index = curr_player_values.index(max_value)
        # max_index_err = children_values_errors[max_index]["err"]
        opt_md = utils.get_max_indexes(curr_player_values)

        errors = [children_values_errors[i]["err"] for i in xrange(len(children_values_errors))]
        current_player_err_rate = self.__evaluator.error_rates[curr_player]

        # D node type
        if self.is_loss(max_value) :
            mult_errors_complements = utils.mult_list([(1 - i) for i in errors])
            agg_err = min((1-mult_errors_complements), current_player_err_rate)

        # D' node type
        else :
            not_opt_md = [i for i in xrange(len(curr_player_values)) if i not in opt_md]
            opt_md_mult = utils.mult_list([errors[i] for i in opt_md])
            not_opt_md_mult = utils.mult_list([errors[i] for i in not_opt_md])
            agg_err = min(opt_md_mult * not_opt_md_mult, current_player_err_rate)

        cur_val, cur_err = self.__evaluator.evaluate(board, curr_player)

        print agg_err, cur_err
        if cur_val[curr_player] == max_value :
            return (cur_val, min(cur_err, agg_err))
        elif cur_err >= agg_err :

            # Non pathological case : using max-n
            return (children_values_errors[max_index]['val'], agg_err)
        else :
            # Pathological case : using static result
            return (cur_val, cur_err)

    def get_moves_history(self):
        return self.__moves_history

    def is_loss(self,value):
        return (value == 0)

