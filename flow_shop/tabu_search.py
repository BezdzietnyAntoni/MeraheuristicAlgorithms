from .flow_shop import *
from enum import Enum
from typing import Union
from itertools import permutations
import random


class TabuList:
        def __init__(self, length: int) -> None:
            self.length = length
            self.tabu_list = [{'action': 0, 'indexes': [0,0]} for i in range(length)]
            self.current_index = 0 

        def __contains__(self, operation):
            return operation in self.tabu_list

        def push(self, operation: dict):
            self.tabu_list[self.current_index] = operation
            self.current_index = (self.current_index+1)%self.length


class TabuSearch:
    POSSIBLE_ACTIONS = {
            0: swap,
            1: reverse_subsequence,
            2: insert_before,
            3: insert_after
        }

    class PossibleSearch(Enum):
        ALL = 1
        HALF_RANDOM = 2
        RANDOM = 3


    def __init__(self, actions: dict, possible_search: PossibleSearch, tabu_length: int = 5 ) -> None:
        self.__parse_actions_dict(actions)
        self.possible_search = possible_search 
        self.tabu_list = TabuList(tabu_length)
        

    def __parse_actions_dict(self, actions: dict):
        self.actions = actions
        self.actions_keys = list(actions.keys)

    def __generate_neighbor(self, type: PossibleSearch, n_jobs: int, random_size: int = None):
        neighbor_type = {
            TabuSearch.PossibleSearch.ALL: self.__generate_neighbor_all,
            TabuSearch.PossibleSearch.HALF_RANDOM: self.__generate_neighbor_half,
            TabuSearch.PossibleSearch.RANDOM: self.__generate_neighbor_random
        }
        neighbor_type[type](n_jobs, random_size)
        
    def __generate_neighbor_all(self, n_jobs: int, random_size: int = None):
        pass

    def __generate_neighbor_half(self, n_jobs: int, random_size: int = None):
        #Random first index 
        idx = random.randint(0, n_jobs-1)
        variants = [i for i in range(n_jobs)].pop(idx)

        for v in variants:
            indexes = [idx, variants]
            if self.actions[0] in [0,1]:
                indexes.sort()
        

        

    def __generate_neighbor_random(self, n_jobs: int, random_size: int = None):
        return [self.__generate_neighbor_options(n_jobs) for _ in range(random_size)]

    def __generate_neighbor_options(self, n_jobs):    
        action = random.choice(self.actions_keys) # Roll action on set
        indexes = self.__generate_n_different_value(2, 0, n_jobs-1) # Roll 2 indexes
        if action in [0,1]: #If action is fs.swap or fs.reverse_subsequence then sort indexes
            indexes.sort()

        return {'action': action, 'indexes': indexes}

    def __generate_n_different_value(self, n_values: int, min_value: int, max_value: int):
        if (max_value - min_value + 1) < n_values:
            raise ValueError("Incorrect range value")

        values = list()
        while len(values) < n_values:
            value = random.randint(min_value, max_value)
            if value not in values:
                values.append(value)
        
        return values



    def get_possible_actions(self):
        return TabuSearch.POSSIBLE_ACTIONS

    
    