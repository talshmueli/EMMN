__author__ ="Tal"

from Boards.NimBoard import NimBoard
from Boards.SplittingGameBoard import SplittingGameBoard
from Boards.SplittingGameBoard1 import SplittingGameBoard1
from Players.MaxnPlayer import MaxnPlayer
from Players.MaxnPlayerAdapter import MaxnPlayerAdapter
from Players.RandomPlayer import RandomPlayer
from Players.EMMNPlayer import EMMNPlayer
from Players.EMMNPlayerExtended import EMMNPlayerExtended
from Evaluators.MaxNEvaluator import  MaxNEvaluator
from Evaluators.ArtificialStaticEvaluator import ArtificialStaticEvaluator
from Evaluators.ErrorArtificialStaticEvaluator import ErrorArtificialStaticEvaluator
from Evaluators.ErrorGenericArtificialStaticEvaluator import ErrorGenericArtificialStaticEvaluator
from Evaluators.ErrorArtificialStaticEvaluatorExtended import ErrorArtificialStaticEvaluatorExtended
from Evaluators.ErrorGenericArtificialStaticEvaluatorExtended import ErrorGenericArtificialStaticEvaluatorExtended
from Evaluators.ErrorGenericSplittingGameBoardNaturalStaticEvaluator import ErrorGenericSplittingGameBoardNaturalStaticEvaluator
from Evaluators.GenericSplittingGameBoardNaturalStaticEvaluator import GenericSplittingGameBoardNaturalStaticEvaluator
from utils import LoggerManager,GraphicsManager,utils,ProcessManager
from Engine import Engine
import copy
import random
import numpy as np
import sys
import getopt
import os
import pickle
import logging
import logging.handlers
from optparse import OptionParser
import shutil
import copy_reg
import types
import traceback

OUTPUT_FILES_DIR = "Outputs"
INF_DEPTH = 2000
DEBUG = True

def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break

    return func.__get__(obj, cls)

def main1() :
    '''
    board = SplittingGameBoard1(6,4)
    evaluator = ErrorGenericSplittingGameBoardNaturalStaticEvaluator(4)

    print str(board)
    print board.get_player_counter(0)
    print board.get_player_counter(1)
    print board.get_player_counter(2)
    print board.get_player_counter(3)
    print board.get_total_cells()
    print evaluator.evaluate(board,1)
    '''

    board = NimBoard(3,2,3)
    print board
    evaluator = MaxNEvaluator(3)
    evaluator_2  = ErrorGenericArtificialStaticEvaluatorExtended(3, [0.1, 0, 0.3])

    for i in xrange(3) :
        print evaluator.evaluate(board, i)
        print evaluator_2.evaluate(board, i)


def main2() :
    make_static_experiment = False
    logger.debug("Searching for EMMNV Error vector")

    if "Nim" == game :
        init_board = NimBoard(3,2,4)
    else :
        init_board = SplittingGameBoard1(8,3)

    dump(init_board)
    if find_emmnv_vector :
        emmv_error_vector = find_better_error_vector(init_board, emmn_error, emmnv_vector_depth, 2)
        logger.debug("EMMNV Error Vector found")
    else :
        emmv_error_vector = get_random_error_vector(3)
        logger.debug("EMMNV Error vector randomized")

    logger.info(emmv_error_vector)
    dump(emmv_error_vector)

    # Iterate on all sizes
    for i in xrange(min_size,max_size+1,1) :

        # Create boards pool for the selected game
        if "Nim" == game :
            boards_pool = [NimBoard(i,2,8) for x in xrange(samples_num)]
        else :
            boards_pool = [SplittingGameBoard1(i*2,3) for x in xrange(samples_num)]

        winners_record = {}

        for depth in xrange(min_depth, max_depth+1,1) :
            winners_record[depth] = []
            dump(depth)
            logger.debug("Running new experiment session")
            logger.info("Running on %d samples (boards)" % (len(boards_pool,)))
            logger.info("Board sizes is %d max depth is %d" % (i,depth,))

            experiments = {}
            for idx, b in enumerate(boards_pool, start=1) :
                board = copy.deepcopy(b)
                logger.info("Running on new board (sample %d of %d) :" % (idx, len(boards_pool),))
                winner = experiment1(b,emmn_error, emmv_error_vector,depth)
                print "The Winner is %s" % (winner, )
                winners_record[depth].append(winner)

            logger.info(winners_record)

            # plot player statistics to screen
            # grapher.plot_winners_statistics(winners_record, i, depth)
            # grapher.save_figure_to_file("winners_%s" % (str(i),))

def main() :
    make_static_experiment = False
    logger.debug("Searching for EMMNV Error vector")

    if "Nim" == game :
        init_board = NimBoard(2,2,4)
    else :
        init_board = SplittingGameBoard1(8,3)

    dump(init_board)
    if find_emmnv_vector :
        emmv_error_vector = find_better_error_vector(init_board, emmn_error, emmnv_vector_depth)
        logger.debug("EMMNV Error Vector found")
    else :
        emmv_error_vector = get_random_error_vector(3)
        logger.debug("EMMNV Error vector randomized")

    logger.info(emmv_error_vector)
    dump(emmv_error_vector)

    # Iterate on all sizes
    for i in xrange(min_size,max_size+1,1) :

        # Create boards pool for the selected game
        if "Nim" == game :
            boards_pool = [NimBoard(i,2,8) for x in xrange(samples_num)]
        else :
            boards_pool = [SplittingGameBoard1(i*2,3) for x in xrange(samples_num)]

        # Init depth globals
        depth_global_moves_counter = {}
        depth_global_total_moves = {}

        # Init total moves counters
        for board in boards_pool :
            depth_global_total_moves[hash(board)] = []

        for depth in xrange(min_depth, max_depth+1,1) :
            dump(depth)
            logger.debug("Running new experiment session")
            logger.info("Running on %d samples (boards)" % (len(boards_pool,)))
            logger.info("Board sizes is %d max depth is %d" % (i,depth,))

            cmo_moves_ration = [0] * len(boards_pool)
            experiments = {}
            for idx, b in enumerate(boards_pool, start=1) :
                board = copy.deepcopy(b)
                logger.info("Running on new board (sample %d of %d) :" % (idx, len(boards_pool),))
                logger.info("\n%s" % (board,))

                dump(board)
                #experiments[init_board] = experiment(init_board, emmn_error, emmv_error_vector, depth)

                if make_static_experiment :
                    correct_moves_counter, total_moves = experiment_static(board, depth)
                else :
                    correct_moves_counter, total_moves = experiment(board, emmn_error, emmv_error_vector, depth)
                    #correct_moves_counter, total_moves = experiment_engine_2(board, emmn_error, emmv_error_vector, depth)

                # correct_moves_ratio = [correct_moves_counter[p] / float(total_moves) for p in correct_moves_counter.keys()]
                # cmo_moves_ratio = list(np.add(correct_moves_counter, correct_moves_ratio))

                depth_global_total_moves[hash(b)] += [total_moves]

                if depth_global_moves_counter == {} :
                    # Init the global moves counter - players and boards

                    for p in correct_moves_counter.keys() :
                        depth_global_moves_counter[p] = {}


                for player in correct_moves_counter.keys() :
                    if not hash(b) in depth_global_moves_counter[p].keys() :
                            depth_global_moves_counter[player][hash(b)] = []

                    depth_global_moves_counter[player][hash(b)] += [correct_moves_counter[player]]

            # plot player statistics to screen
            grapher.plot_players_statistics(depth_global_moves_counter, depth_global_total_moves, min_depth, depth, i, boards_pool, emmn_error)
            grapher.save_figure_to_file("%s" % (str(i),))

def start_game(board, players) :
    logger.info("Initial Board : \n%s" % (board,))
    e = Engine(board, players)
    return e.run_game()

def print_summary(players, perfect_players) :
    print "Game Summary : \n"
    for p,p1 in zip(players, perfect_players) :
        correct_decisions = 0
        print "Player %s" % (p.player_name, )
        print "Num of decisions made = %s" % (str(len(p.get_moves_history())), )
        for board, move in p.get_moves_history().items() :
            if move == p1.make_move(copy.deepcopy(board), False) :
                correct_decisions += 1
        print "Num of correct decisions = %s" % (str(correct_decisions), )

def find_better_error_vector(init_board, emmn_error, depth, active_players = 3) :
    # Iterate till a better error vector is found
    while True :
        emmv_error_vector = get_random_error_vector(active_players)
        logger.debug("Checking random error vector %s" % (emmv_error_vector,))

        #parasite_EMMNv = EMMNPlayer(0, "EMMNv", depth, ErrorGenericArtificialStaticEvaluator(active_players, emmv_error_vector, endgame_db_file_path),active_players)
        parasite_EMMNv2 = EMMNPlayerExtended(0, "EMMNv", depth, ErrorGenericArtificialStaticEvaluatorExtended(active_players, emmv_error_vector, endgame_db_file_path), active_players)
        #parasite_EMMN  = EMMNPlayer(0, "EMMN", depth, ErrorArtificialStaticEvaluator(active_players, emmn_error, endgame_db_file_path), active_players)
        parasite_EMMN2 = EMMNPlayerExtended(0, "EMMN", depth, ErrorArtificialStaticEvaluatorExtended(active_players, emmn_error, endgame_db_file_path), active_players)
        results, _ = experiment_engine(init_board, [parasite_EMMNv2, parasite_EMMN2], active_players)

        # Check wether EMMNv produces better results
        if results["EMMNv"] > results["EMMN"] :
            break
        elif results["EMMNv"] == results["EMMN"] :
            logger.debug("EMMN got same results")
        else :
            logger.debug("EMMN got better results")

    return emmv_error_vector

def get_random_error_vector(length) :
    return list(np.random.sample(length) * 0.5)

'''
def experiment_engine_2(init_board, emmn_error, emmnv_error_vector):
    active_players = 3

    emmv_error_vector = find_better_error_vector(init_board, emmn_error, emmnv_vector_depth)
    EMMNv_Evaluator = ErrorGenericArtificialStaticEvaluatorExtended(active_players, emmnv_error_vector, endgame_db_file_path)
    EMMN_Evaluator = ErrorArtificialStaticEvaluatorExtended(active_players, emmn_error, endgame_db_file_path)
    Maxn_Limited_Evaluator = ArtificialStaticEvaluator(active_players, emmn_error, endgame_db_file_path)
    Maxn_Evaluator = MaxNEvaluator(active_players, endgame_db_file_path)

    parasite_evaluators = [EMMNv_Evaluator, EMMN_Evaluator, Maxn_Limited_Evaluator]

    print [evaluator.evaluate(init_board, 1) for evaluator in parasite_evaluators]
'''

def experiment_engine(init_board, parasite_players, active_players = 3) :
    init_board_copy = copy.deepcopy(init_board)
    dump(active_players)

    maxn_evaluator = MaxNEvaluator(active_players, endgame_db_path=endgame_db_file_path)

    maxn_player1 = MaxnPlayerAdapter(0, "MaxN", INF_DEPTH, maxn_evaluator, active_players, parasite_players)
    random_player1 = RandomPlayer(1, "Rand1", 10, MaxNEvaluator(active_players), active_players)
    random_player2 = RandomPlayer(2, "Rand2", 10, MaxNEvaluator(active_players), active_players)

    '''
    maxn_player2 = MaxnPlayer(1, "MaxN_1", INF_DEPTH, maxn_evaluator, active_players)
    maxn_player3 = MaxnPlayer(2, "MaxN_2", INF_DEPTH, maxn_evaluator, active_players)
    '''

    players = [maxn_player1, random_player1, random_player2]
    dump([p.player_name for p in players])
    # Game1
    start_game(init_board_copy, players)
    maxn_history = maxn_player1.moves_history
    dump(maxn_history)
    '''
    print maxn_history
    for player in parasite_players :
        print player.player_name
        print player.get_moves_history()
    '''

    ## Accuracy Calculation ##
    # initialize all correct moves counters
    correct_moves_counters = {}
    for player in parasite_players :
        correct_moves_counters[player.player_name] = 0


    # update correct moves counters
    for player in parasite_players :
        moves_history = player.get_moves_history()
        for board in moves_history :
            # If the parasite player keep history of lists, then check for the intersection
            if isinstance(moves_history[board], list) :
                if moves_history[board][0] in maxn_history[board] :
                    correct_moves_counters[player.player_name] += 1
                '''
                if len(set.intersection(set(moves_history[board]), set(maxn_history[board]))) > 0 :
                    correct_moves_counters[player.player_name] += 1
                '''

            elif moves_history[board] in maxn_history[board] :
                correct_moves_counters[player.player_name] += 1

    logger.info("Summary :")
    for player_name in correct_moves_counters :
        correct_moves = correct_moves_counters[player_name]
        total_moves = len(maxn_history)
        correct_moves_ratio = (float(correct_moves) / total_moves) * 100
        logger.info("Player %s - %s out of %s (%s %%)" % (player_name, str(correct_moves), str(total_moves), str(int(correct_moves_ratio))))
    dump(correct_moves_counters)

    return correct_moves_counters, total_moves

def winner_experiment_engine(init_board, parasite_players) :
    init_board_copy = copy.deepcopy(init_board)

    # maxn_evaluator = MaxNEvaluator(active_players, endgame_db_path=endgame_db_file_path)
    # maxn_player1 = MaxnPlayer(0, "MaxN", INF_DEPTH, maxn_evaluator, active_players)

    '''
    maxn_player2 = MaxnPlayer(1, "MaxN_1", INF_DEPTH, maxn_evaluator, active_players)
    maxn_player3 = MaxnPlayer(2, "MaxN_2", INF_DEPTH, maxn_evaluator, active_players)
    '''

    dump([p.player_name for p in parasite_players])

    # Game1
    winner = start_game(init_board_copy, parasite_players)

    return winner

def experiment_static(init_board, depth) :
    active_players = 3

    #Define Parasite players
    parasite_EMMNv2 = EMMNPlayerExtended(0, "EMMNv_Extended", depth, ErrorGenericSplittingGameBoardNaturalStaticEvaluator(active_players), active_players)
    parasite_EMMN2 = EMMNPlayerExtended(0, "EMMN_Extended", depth, ErrorGenericSplittingGameBoardNaturalStaticEvaluator(active_players), active_players)
    parasite_MaxN  = MaxnPlayer(0, "MaxN-Limited", depth, GenericSplittingGameBoardNaturalStaticEvaluator(active_players), active_players)

    parasite_players = [parasite_EMMN2, parasite_EMMNv2, parasite_MaxN]

    dump([player.player_name for player in parasite_players])
    return experiment_engine(init_board, parasite_players)

def experiment(init_board,emmn_error, emmv_error_vector, depth) :
    active_players = 3

    #Define Parasite players
    #parasite_EMMNv = EMMNPlayer(0, "EMMNv", depth, ErrorGenericArtificialStaticEvaluator(active_players, emmv_error_vector, endgame_db_file_path),active_players)
    parasite_EMMNv2 = EMMNPlayerExtended(0, "EMMNv_Extended", depth, ErrorGenericArtificialStaticEvaluatorExtended(active_players, emmv_error_vector, endgame_db_file_path), active_players)
    #parasite_EMMN  = EMMNPlayer(0, "EMMN", depth, ErrorArtificialStaticEvaluator(active_players, emmn_error, endgame_db_file_path), active_players)
    parasite_EMMN2 = EMMNPlayerExtended(0, "EMMN_Extended", depth, ErrorArtificialStaticEvaluatorExtended(active_players, emmn_error, endgame_db_file_path), active_players)
    parasite_MaxN  = MaxnPlayer(0, "MaxN-Limited", depth, ArtificialStaticEvaluator(active_players, emmn_error, endgame_db_file_path), active_players)

    #parasite_MaxN3  = MaxnPlayer(0, "MaxN_3", 3, ArtificialStaticEvaluator(active_players, emmn_error), active_players)
    #parasite_MaxN10  = MaxnPlayer(0, "MaxN_10", 10, ArtificialStaticEvaluator(active_players, emmn_error), active_players)

    parasite_players = [parasite_EMMN2, parasite_EMMNv2, parasite_MaxN]
    #parasite_players = [parasite_EMMN, parasite_EMMNv]
    dump([player.player_name for player in parasite_players])
    return experiment_engine(init_board, parasite_players)

def experiment1(init_board, emmn_error,  emmnv_error_vector, depth) :
    active_players = 3

    MaxN  = MaxnPlayer(0, "MaxN-Limited", depth, ArtificialStaticEvaluator(active_players, emmn_error, endgame_db_file_path), active_players)
    EMMNv2 = EMMNPlayerExtended(1, "EMMNv_Extended", depth, ErrorGenericArtificialStaticEvaluatorExtended(active_players, emmnv_error_vector, endgame_db_file_path), active_players)
    Maxn2 = MaxnPlayer(2, "MaxN-Limited", depth, ArtificialStaticEvaluator(active_players, emmn_error, endgame_db_file_path), active_players)

    winner = winner_experiment_engine(init_board, [MaxN, EMMNv2, Maxn2])

    if winner == 0 :
        return "MaxN"
    elif winner == 1 :
        return "EMMNv"
    else :
        return "Other"

def log(s):
    logger.info(s)

def dump(s):
    pickle.dump(s, dump_file)
    dump_file.flush()
    os.fsync(dump_file.fileno())

if __name__ == "__main__" :
    # Init option parser
    parser = OptionParser()
    parser.add_option("-t", "--tag", type = "string", dest = "tag", help="run tag name (for outputs)")
    parser.add_option("-g", "--game", type = "string", dest = "game", default = "Nim", help="Choose game")
    parser.add_option("-n", "--min-size", type = "int", dest = "min_size", help = "minimum experiment nim board size")
    parser.add_option("-d", "--max-depth", type = "int", dest = "max_depth", help ="maximum game experiments depth")
    parser.add_option("-m", "--min-depth", type = "int", dest = "min_depth", default = 1, help ="minimum game experiments depth")
    parser.add_option("-e", "--emmn-error", dest = "emmn_error", default = 0.2, help = "set emmn constant error value")
    parser.add_option("-a", "--find-emmnv-vector-depth", dest = "emmnv_vector_depth", help = "set emmnv vector search algorithm depth")
    parser.add_option("-x", "--max-size", type = "int", dest = "max_size", help = "maximum experiment nim board size")
    parser.add_option("-f", "--find-emmnv-vector", action = "store_true", dest = "find_emmnv_vector", default = False, help = "dynamically find better emmnv vector")
    parser.add_option("-q", "--quiet", action = "store_false", dest = "verbose", default = True, help = "don't print debug messages to stdout")
    parser.add_option("-o", "--override", action = "store_true", dest = "override", default = False, help = "override output directory if exists")
    parser.add_option("-s", "--samples", dest = "samples_num", default = 5, help = "set the number of samples (Boards) per depth (default 5)")
    parser.add_option("-b", "--db-file",type = "string", dest = "db_file_path", help = "Load EndGame Database file if exists")

    (options, args) = parser.parse_args()

    if not (options.emmnv_vector_depth and options.tag and options.max_size and options.min_size and options.max_depth and options.override) :
        parser.print_help()
        parser.error("Required variable missing")

    # Make output files directory
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), OUTPUT_FILES_DIR, options.tag)
    if os.path.isdir(dir_path) :
        if bool(options.override) :
            if utils.query_yes_no("Removing exsiting dir %s, Do you agree ?" % (options.tag,)) :
                shutil.rmtree(dir_path)
        else :
            parser.error("Output directory already exists (Add -o to override dir)")

    os.mkdir(dir_path)

    # Write options to file
    options_file_path = log_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),OUTPUT_FILES_DIR, options.tag,"options.txt")
    options_file = file(options_file_path, "wb")
    options_file.write(str(options))
    options_file.close()

    # Init loggers
    logger = LoggerManager.getLogger("main_log")
    console_formatter = logging.Formatter('%(name)-8s (%(process)d): %(levelname)-8s | %(message)s')
    file_formatter = logging.Formatter('%(name)-8s (%(process)d): %(levelname)-8s %(asctime)s %(module)s | %(message)s')
    log_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),OUTPUT_FILES_DIR, options.tag,"log.txt")
    log_file_handler = logging.FileHandler(log_file_path)
    log_file_handler.setFormatter(file_formatter)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.debug("Log Started!")

    # Init graphers
    output_graph_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),OUTPUT_FILES_DIR, options.tag,"graph")
    grapher = GraphicsManager(output_graph_path)

    # Fill options to variables
    if options.verbose :
        logger.level = logging.DEBUG
    else :
        logger.level = logging.INFO

    logger.addHandler(log_file_handler)
    logger.addHandler(console_handler)
    dump_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),OUTPUT_FILES_DIR, options.tag,"dump")
    min_size = options.min_size
    max_size = options.max_size
    samples_num = int(options.samples_num)
    max_depth = options.max_depth
    min_depth = options.min_depth
    game = options.game
    find_emmnv_vector = options.find_emmnv_vector
    emmnv_vector_depth = int(options.emmnv_vector_depth)
    emmn_error = float(options.emmn_error)
    dump_file = file(dump_file_path, "wb")

    if options.db_file_path :
        logger.info("End game DB present %s" % (options.db_file_path,))
        endgame_db_file_path = options.db_file_path
    else :
        endgame_db_file_path = None
    try :
        # main()
        main2()

    except KeyboardInterrupt :
        logger.debug("Program interrupted by user")
    #except Exception, e:
    #    logger.debug("Fatal Error : %s" % (e,))

    finally:
        # Close & Clean
        dump_file.close()
        ProcessManager.cleanPool()

        # Zip all products
        zip_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),OUTPUT_FILES_DIR, options.tag + ".zip" )
        utils.zipdir(os.path.join(os.path.dirname(os.path.realpath(__file__)),OUTPUT_FILES_DIR, options.tag), zip_file_path)
        copy_reg.pickle(types.FunctionType, _pickle_method, _unpickle_method)