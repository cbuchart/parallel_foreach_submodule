# -*- coding: utf-8 -*-

from parallelforeachsubmodule.metadata import Metadata
from parallelforeachsubmodule.process import PFSProcess
import argparse
import threading
import os
import re
import time


def worker(submodule_list, path, command):
    for submodule in submodule_list:
        PFSProcess(submodule, path, command).run()


class PFS(object):
    def __init__(self):
        self.meta = Metadata()
        self.__threads = list()

        # Parse arguments provided
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--version', action='version', version=self.meta.get_version())
        parser.add_argument('-p', '--path', dest='path', help='System path where start execution',
                            type=self.exists_path, default=".")
        parser.add_argument('-c', '--command', dest='command', help='Git command',
                            type=self.empty_cmd, default="")
        parser.add_argument('-j', '--jobs', dest='jobs',
                                      help='Number of concurrent jobs', type=int, default=1)
        self.args = parser.parse_args()

        self.__submodule_path_pattern = re.compile('path ?= ?([A-za-z0-9-_]+)(\/[A-za-z0-9-_]+)*([A-za-z0-9-_])')
        self.__path_pattern = re.compile(' ([A-za-z0-9-_]+)(\/[A-za-z0-9-_]+)*([A-za-z0-9-_])')

    @staticmethod
    def exists_path(path):
        if not os.path.isdir(path):
            raise argparse.ArgumentTypeError("%s is not valid path" % path)
        return path

    @staticmethod
    def empty_cmd(cmd):
        if cmd == "":
            raise argparse.ArgumentTypeError("git cmd is empty")
        return cmd

    def read_submodules(self, file):
        submodules = list()
        for line in file:
            submodule_path = re.search(self.__submodule_path_pattern, line)
            if submodule_path:
                path = re.search(self.__path_pattern, submodule_path.group())
                if path:
                    submodules.append(path.group()[1:])  # Remove space at first position
        return submodules

    def run(self):
        start_time = time.time()
        if not os.path.exists(os.path.join(self.args.path, '.gitmodules')):
            print("File .gitmodules not found")
            exit(0)

        with open(os.path.join(self.args.path, '.gitmodules')) as f:
            submodules = self.read_submodules(f)

        print(str(len(submodules)) + " submodules")

        list_submodule_list = list()
        num_jobs = 0
        while num_jobs < self.args.jobs:
            list_submodule_list.append(list())
            num_jobs += 1

        i = 0
        for submodule in submodules:
            list_submodule_list[i % num_jobs].append(submodule)
            i += 1

        #print(list_submodule_list)

        print("Running with " + str(num_jobs) + " threads...")
        for i in range(num_jobs):
            t = threading.Thread(target=worker, args=(list_submodule_list[i], self.args.path, self.args.command,))
            self.__threads.append(t)
            t.start()

        for i in range(num_jobs):
            self.__threads[i].join()

        print("Execution complete!")
        print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    pfs = PFS()
    pfs.run()