from __future__ import annotations
import pandas as pd
from pandas import DataFrame

from dataclasses import dataclass

from typing import *

from pcf import Pcf

DATE_COLUMN_NAME = '[TIME] TIMESTAMP / RECORD ID'



class MyCsv:

    def __init__(self, csv_path, pcf_config:Pcf) -> None:
        self.results_csv_path = csv_path
        self.pcf:Pcf = pcf_config
        self.df:DataFrame = None
        self._update_df()
    
    @property
    def records(self) -> list[Record]:
        return [self.Record(self, self.df.iloc[idx]) for idx in self.df.index]



    def _to_datetime(self):
        self.df[DATE_COLUMN_NAME] = pd.to_datetime(self.df[DATE_COLUMN_NAME], format='%Y-%m-%d_%H:%M:%S.%f')
    
    def get_last_record(self) -> Record:
        self._update_df()
        return self.Record(self, self.df.iloc[self.df[DATE_COLUMN_NAME].argmax()])
    
    def _update_df(self):
        self.df = pd.read_csv(self.results_csv_path, sep=',')
        self._to_datetime()
    
    class Record:

        def __init__(self, csv, data:pd.Series) -> None:
            self.results:MyCsv = csv
            self.data:pd.Series = data
            self.date = data.get(DATE_COLUMN_NAME)

        @property
        def tests(self) -> list[Test]:
            return [self.Test(self, test_name, self.data.get(test_name)) for test_name in self.data.keys()]
        
        def __getitem__(self, test_name:str) -> Test:
            for test in self.tests:
                if test_name == test.name:
                    return test
            raise KeyError(test.name)
        
        def __repr__(self) -> str:
            return repr(self.data)
        
        def _get_failed_tests(self) -> list[Test]:
            return [self.Test(self, test_name, self.data.get(test_name)) for test_name in self.data.keys() if "FAIL" in str(self.data.get(test_name))]

        def get_failstring(self):
            for test in self._get_failed_tests():
                print("limits for failed test: ", test.limits)
        
        


        class Test:

            def __init__(self, outer, name, data) -> None:
                self.name = name
                self.data = data
                if not isinstance(outer, MyCsv.Record):
                    raise TypeError(f"exp type: {MyCsv.Record}, recv type {type(outer)}")
                self._outer = outer

            
            @property
            def record(self) -> MyCsv.Record:
                return self._outer

            @property
            def t_type(self):
                pass

            
            @property
            def limits(self) -> Limits:
                return self.record.results.pcf["TEST RESULTS SPECIFICATIONS"][self.name]
                return self._limits 
                   

            @dataclass
            class Limits:
                low: float
                high:float
            
            def __repr__(self) -> str:
                return f'{self.name} : {self.data}'
    
    
    
