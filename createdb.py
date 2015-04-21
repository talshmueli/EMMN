__author__ = 'Tal'

import pickle
import os
from Boards.NimBoard import NimBoard
from optparse import OptionParser
from utils import CustomizedProgressBar

def read_endgame_db(db_file_path) :
    f = file(db_file_path, "rb")
    db = {}

    try :
        while True :
            board, player = pickle.load(f)
            maxn_value = pickle.load(f)
            db[(board,player)] = maxn_value
    except EOFError :
        pass
    except :
        print "Some parsing error occurred"

    f.close()
    return db

    
def create_endgame_db(db_file_path, players_num, max_num_of_heaps, lower_bound, upper_bound) :
    
    from Evaluators.MaxNEvaluator import MaxNEvaluator
    
    f = file(db_file_path, "wb")
    m = MaxNEvaluator(players_num)
    p = CustomizedProgressBar()


    for heaps_num in p(range(max_num_of_heaps)) :
        print "Building DB for board with %d heaps now :" % (heaps_num,)
        for player in xrange(players_num) :
            boardIterator = NimBoard.generate_boards_generator(heaps_num+1,lower_bound,upper_bound)
            for b in boardIterator :
                val = m.evaluate(b,player)
                # Dump data to file
                pickle.dump((b, player), f)
                pickle.dump(val, f)
                f.flush()
                os.fsync(f.fileno())

    print "End Game DataBase was successfully created !"
    f.close()

def main() :
    print "Now creating EndGame DB"
    create_endgame_db(db_file, players_num, heaps_num, lower_bound, upper_bound)


if __name__ == "__main__" :

    parser = OptionParser()
    parser.add_option("-p", "--db_file_path", type = "string", dest = "db_file_path", help="path to write/read db")
    parser.add_option("-n", "--players_num", type = "string", dest = "players_num", default = "3", help="Number of players")
    parser.add_option("-e", "--heaps_num", type = "string", dest = "heaps_num", help = "Maximum number of Nim game heaps/cols")
    parser.add_option("-l", "--lower_bound", type = "string", dest = "lower_bound", help ="lower bound on the number of elements in each heap")
    parser.add_option("-u", "--upper_bound", type = "string", dest = "upper_bound", help ="upper bound on the number of elements in each heap")

    (options, args) = parser.parse_args()

    if not (options.db_file_path and options.heaps_num and options.lower_bound and options.upper_bound) :
        parser.print_help()
        parser.error("Required variable missing")

    # Load options to local variables
    db_file = options.db_file_path
    players_num = int(options.players_num)
    heaps_num = int(options.heaps_num)
    lower_bound = int(options.lower_bound)
    upper_bound = int(options.upper_bound)

    main()
