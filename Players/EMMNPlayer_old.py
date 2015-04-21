__author__ = 'Tal'

import copy
from Players.Player import Player
from utils import utils


class EMMNPlayer(Player) :
    def __init__(self, player_num, player_name, depth, evaluator, players_num) :
        super(EMMNPlayer, self).__init__(player_name)
        self.__player_num = player_num
        self.__depth = depth
        self.__evaluator = evaluator
        self.__players_num = players_num
        self.__moves_history = {}

    def make_move(self, board):

        child_values_errors = []
        moves = board.get_next_moves(self.__player_num)

        print "Possible moves : %s" % (len(moves),)
        for move in moves :
            b_copy = copy.deepcopy(board)
            b_copy.make_move(*move)
            next_player = (self.__player_num + 1) % self.__players_num
            val, err = self.emmn_search(b_copy, self.__depth - 1 , next_player)
            child_values_errors.append({"val" : val, "err" : err})

        # Achieve max value for current player with minimum error value
        curr_player_values = [child_values_errors[i]["val"][self.__player_num] for i in xrange(len(child_values_errors))]
        max_value = max(curr_player_values)
        max_values_errors_set = [child_values_errors[i]["err"] for i in xrange(len(curr_player_values)) if curr_player_values[i] == max_value]
        max_value_min_error_index = max_values_errors_set.index(min(max_values_errors_set))

        # Log move and return
        self.__moves_history[copy.deepcopy(board)] = moves[max_value_min_error_index]
        return moves[max_value_min_error_index]

    def emmn_search(self, board, depth, curr_player) :
        children_values_errors = []

        # if the game is over or we reached the limited depth,
        # then we return the evaluation function value on that node
        if board.is_game_over() or depth == 0 :
            return self.__evaluator.evaluate(board, curr_player)

        # determine children values and aggErrs
        for move in board.get_next_moves(curr_player):
            b_copy = copy.deepcopy(board)
            b_copy.make_move(*move)
            next_player = (curr_player + 1) % self.__players_num
            val, err = self.emmn_search(b_copy, depth - 1 , next_player)
            children_values_errors.append({"val" : val, "err" : err})


        curr_player_values = [children_values_errors[i]["val"][self.__player_num] for i in xrange(len(children_values_errors))]
        # max_value = max(curr_player_values)
        # Todo - check wether we should choose the minimum error from a set of errors
        # max_index = curr_player_values.index(max_value)
        # max_index_err = children_values_errors[max_index]["err"]
        opt_md = self.get_max_indexes(curr_player_values)

        N = self.__players_num
        errors = [children_values_errors[i]["err"] for i in xrange(len(children_values_errors))]
        s = utils.sum_except([1 - errors[i] + errors[i]*(N-2)/(N-1) for i in xrange(len(errors))], max_index)

        if self.is_loss(max_value) :
            agg_err = 1 -(1 - max_index_err) * s
        else :
            agg_err = (1 - max_index_err)
            for child_values_error in children_values_errors :
                if not(self.is_loss(child_values_error['val'][self.__player_num])) :
                    agg_err = agg_err * child_values_error['err']
                else :
                    agg_err = agg_err * (1 - child_values_error['err'] + child_values_error['err']*(N-2)/(N-1))


        cur_val, cur_err = self.__evaluator.evaluate(board, curr_player)
        if cur_val == max_value :
            return (cur_val, min(cur_err, agg_err))
        elif cur_err >= agg_err :
            # Non pathological case : using max-n
            return (children_values_errors[max_index]['val'], agg_err)
        else :
            # Pathological case : using static result
            return (cur_val, cur_err)


    def get_max_indexes(self, a):
        max = max(a)
        max_indexes = [i for i, v in enumerate(a) if v == max]
        return max_indexes

    def get_moves_history(self):
        return self.__moves_history

    def is_loss(self,value):
        return (value == 0)