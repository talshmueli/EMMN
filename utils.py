import multiprocessing

__author__ = 'Tal'

from progressbar import *
from typedecorator import *
import logging
import numpy as np
import matplotlib.pyplot as plt
import zipfile
import os
import copy_reg
import types
import pickle
import copy
import traceback
from multiprocessing import Pool, Manager, Queue

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def apply_async(method, args):
    return ProcessManager.getPool().apply_async(method, args)

def _pickle_file(f) :
    return _unpickle_file, (f.name, f.mode)

def _unpickle_file(name, mode) :
    f = open(name, mode)
    return f

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

# Change some of the pickling methods used by Pickle
copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
copy_reg.pickle(types.FileType, _pickle_file, _unpickle_file)

class utils(object) :

    @staticmethod
    def sum_except(sum_list, index) :
        s = sum(sum_list) - sum_list[index]
        return s

    @staticmethod
    def zipdir(path, zip_name):
        zip = zipfile.ZipFile(zip_name, 'w')
        for root, dirs, files in os.walk(path):
            for file in files:
                zip.write(os.path.join(root, file))

    @staticmethod
    def mult_list(l):
        # if list is empty the multipication is 1
        if 0 == len(l) :
            return 1
        else :
            return reduce(lambda x,y : x*y, l)

    @staticmethod
    def get_max_indexes(l):
        m = max(l)
        max_indexes = [i for i, v in enumerate(l) if v == m]
        return max_indexes

    @staticmethod
    def query_yes_no(question, default="yes"):
        """Ask a yes/cdno question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = raw_input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n")

    @staticmethod
    def average_map_of_lists(map_of_lists):
        a = map_of_lists
        result = [sum([a[i][j] for i in a.keys()])/float(len(a.keys())) for j in xrange(len(a[a.keys()[0]]))]
        return result

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances.keys():
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class MemCache(dict):
    def __init__(self, fn, name, db_file_path = None, db_file_parser_func = None):
        dict.__init__(self)
        self.__fn = fn
        self.__name = name
        self.__logger = LoggerManager.getLogger("main_log")
        if not db_file_path is None :
            self.__db_file_path = db_file_path
            self.__db_file_parser_func = db_file_parser_func
            self.init_from_file()
            self.__logger.debug("Memcache %s :: Initialized from file (%d records)" % (self.__name, self.__len__()))


    def __reduce__(self):
        return (self.__class__, (self.__fn, self.__name))

    def __getitem__(self, item):

        if item in self.keys():
            return dict.__getitem__(self, item)
        else:
            dict.__setitem__(self, item, self.__fn(*item))
            if self.__len__() % 1000 == 0 and self.__len__() != 0  :
                self.__logger.debug("MemCache %s Size Report : %d" % (self.__name, self.__len__()))
            return dict.__getitem__(self, item)

    def init_from_file(self):
        db_dict = self.__db_file_parser_func(self.__db_file_path)
        for item in db_dict :
            dict.__setitem__(self, item, db_dict[item])

    def __setitem__(self, key, value):
        if self.__len__() % 1000 == 0 and self.__len__() != 0  :
            self.__logger.debug("MemCache %s Size Report : %d" % (self.__name, self.__len__()))
        if self.has_key(key) :
            pass
        else :
            return dict.__setitem__(self, key,value)

class MemCacheSingleton(object) :
    __metaclass__ = Singleton
    _memcaches = {}

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def getMemCache(name, fn, db_file_path = None, db_file_parser_func = None):
        if name not in MemCacheSingleton._memcaches.keys():
            LoggerManager.getLogger("main_log").debug("New MemCache created : %s" % (name,))
            MemCacheSingleton._memcaches[name] = MemCache(fn, name, db_file_path, db_file_parser_func)
        return MemCacheSingleton._memcaches[name]

class CustomizedProgressBar(ProgressBar) :
    def __init__(self) :
        widgets = [FormatLabel(''), ' ', Percentage(), ' ', Bar('#'), ' ', RotatingMarker()]
        super(CustomizedProgressBar, self).__init__(widgets = widgets)

class LoggerManager(object):
    __metaclass__ = Singleton

    _loggers = {}
    def __init__(self, *args, **kwargs):
        pass

    def __reduce__(self):
        pass

    @staticmethod
    def getLogger(name=None):
        if not name:
            logging.basicConfig()
            return logging.getLogger()
        elif name not in LoggerManager._loggers.keys():
            LoggerManager._loggers[name] = logging.getLogger(str(name))
        return LoggerManager._loggers[name]

class ProcessManager(object) :
    __metaclass__ = Singleton

    _pool = None
    _queue = None

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def getQueue():
        if ProcessManager._queue is None :
            LoggerManager.getLogger("main_log").debug("New workers Queue was created successfully")
            ProcessManager._queue = Queue()
        return ProcessManager._queue

    @staticmethod
    def getPool():
        if ProcessManager._pool is None :
            cpu_count = multiprocessing.cpu_count()
            LoggerManager.getLogger("main_log").debug("New Process Pool created successfully (%d Workers)" % (cpu_count,))

            ProcessManager._pool = Pool(processes=cpu_count, initializer=init_worker)
        return ProcessManager._pool

    @staticmethod
    def cleanPool():
        if not ProcessManager._pool is None :
            ProcessManager._pool.close()
            ProcessManager._pool.join()

    @staticmethod
    def getEvent():
        '''
        This function returns a new event for multiprocessing purposes
        '''
        m = Manager()
        return m.Event()


    '''
    @staticmethod
    def apply_async(method, args):
        print "Type is - " + str(type(method))
        copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
        print "Running Apply_Async with params %s" % (str(method),)
        print method
        print pickle.dumps(method)
        return ProcessManager.getPool().apply_async(method, args)
    '''

class GraphicsManager(object):
    def __init__(self, output_path) :
        self.output_path = output_path
        pass

    def plot_players_statistics(self, players_moves_counters , players_total_moves, min_depth, max_depth,size, boards_pool, emmn_error):
        plt.ion()
        plt.cla()
        players_moves_fraction = {}
        for player in players_moves_counters.keys() :
            for board in boards_pool :
                players_moves_fraction[hash(board)] = [float(players_moves_counters[player][hash(board)][i])/players_total_moves[hash(board)][i] for i in xrange(len(players_total_moves[hash(board)]))]

                #print map(lambda x : float(x), range(1,max_depth+1))
            players_moves_fractions_average = utils.average_map_of_lists(players_moves_fraction)

            plt.plot(map(lambda x : float(x), range(min_depth,max_depth+1)), players_moves_fractions_average, label = player)

        plt.title("Fraction of Correct Decisions (Depth %d, Samples %d)\n (e = %f, s = %d)" % (max_depth, len(boards_pool), emmn_error, size))
        plt.legend()
        plt.draw()

    def save_figure_to_file(self, suffix = ""):
        plt.savefig(self.output_path + suffix + ".png")

