"""Module for read and parse data from database OR-Library J.E. Beasley
    http://people.brunel.ac.uk/~mastjjb/jeb/orlib/flowshopinfo.html
Raises:
    IOError: If file is not in example format
"""

import numpy as np

from .data_frame import DataFrame


class DatasetReader:
    """Class reader flow shop problem in format like in OR-Library J.E. Beasley
    http://people.brunel.ac.uk/~mastjjb/jeb/orlib/flowshopinfo.html
    """

    def __init__(self, path):
        self.path = path
        self.lines_in_file = 0
        self.test_count = 0
        self.n_jobs = 0
        self.m_machines = 0
        self.const_line = 3  # Const value lines in test set

        self.__is_file_exist()
        self.__count_line_in_file()
        self.__is_file_correct()
        self.__parse_config_data()
        self.__count_test_in_file()

    # Prepare metadata and basic check file
    def __is_file_exist(self):
        open(self.path, "r", encoding="UTF-8")

    def __count_line_in_file(self):
        self.lines_in_file = sum(1 for line in open(self.path, "r", encoding="UTF-8"))

    def __is_file_correct(self):
        if self.lines_in_file < 4:  # Min lines for 1 machine
            raise IOError("Bad data format")

    def __parse_config_data(self):
        # Read second line
        f = open(self.path, "r", encoding="UTF-8")
        f.readline()
        line = f.readline()
        f.close()

        # Parse
        sline = line.split()
        self.n_jobs = int(sline[0])
        self.m_machines = int(sline[1])

    def __count_test_in_file(self):
        self.test_count = self.lines_in_file / (self.const_line + self.m_machines)

    # Read data
    def __parse_header(self, line, df):
        param = [int(p) for p in line.split()]
        df.n_jobs = param[0]
        df.m_machines = param[1]
        df.init_seed = param[2]
        df.up_bound = param[3]
        df.low_bound = param[4]

    def __normal_parse_processing_time(self, data, df):
        for i, line in enumerate(data):
            p = [int(x) for x in line.split()]
            df.processing_time[i, :] = p

    def __rotate_parse_processing_time(self, data, df):
        self.__normal_parse_processing_time(data, df)
        df.processing_time = list(zip(*(df.processing_time[::-1])[::-1]))

    def __parse_processing_time(self, data, df, rot_data):
        if not rot_data:
            self.__normal_parse_processing_time(data, df)
        else:
            self.__rotate_parse_processing_time(data, df)

    def read_data(self, nth_set: int, rot_data=False) -> DataFrame:
        """Read data from database

        Args:
            nth_set (int): Number of benchmark in file
            rot_data (bool, optional): Rotate time table. Defaults to False.

        Returns:
            DataFrame: Data frame for flow shop problem
        """
        df = DataFrame()

        f = open(self.path, "r", encoding="UTF-8")
        for _ in range(nth_set * (self.m_machines + self.const_line) + 1):
            f.readline()
        header_line = f.readline()
        self.__parse_header(header_line, df)
        df.processing_time = np.zeros((self.m_machines, self.n_jobs))

        f.readline()  # Skip one line
        data = [f.readline() for _ in range(df.m_machines)]
        self.__parse_processing_time(data, df, rot_data)
        f.close()

        return df
