# -*- coding: utf-8 -*-

import subprocess as sub
import os


class PFSProcess(object):
    def __init__(self, submodule, path, cmd):
        self.__submodule = submodule
        self.__path = path
        self.__cmd = cmd
        self.__output = None
        self.__p = None

    def run(self):
        self.__output = "\n\n" + self.__submodule + "\n"
        #self.__output = sub.check_output(self.__cmd)
        self.__p = sub.Popen(self.__cmd, stdout=sub.PIPE, stderr=sub.PIPE, shell=True,
                             cwd=os.path.join(self.__path, self.__submodule))
        self.__output += self.__p.communicate()[0].decode('utf-8')
        print(self.__output)