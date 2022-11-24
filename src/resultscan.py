import pandas as pd
from datetime import datetime
import pcf
from dataclasses import dataclass
from __future__ import annotations
import csv

DATE_C_NAME = '[TIME] TIMESTAMP / RECORD ID' #date_column_name



class CsvResults():

    def __init__(self, csv_path) -> None:
        self.results_csv_path = csv_path
        self.df = None
        self._update_df()
    
    def _to_datetime(self):
        self.df[DATE_C_NAME] = pd.to_datetime(self.df[DATE_C_NAME], format='%Y-%m-%d_%H:%M:%S.%f')
    
    def get_last_record(self) -> Record:
        self._update_df()
        return self.Record(self.df.iloc[self.df[DATE_C_NAME].argmax()])
    
    def _update_df(self):
        self.df = pd.read_csv(self.results_csv_path, sep=',')
        self._to_datetime()
    
    class Record:

        def __init__(self, data:pd.Series) -> None:
            self.data:pd.Series = data
            self.date = data.get(DATE_C_NAME)
        
        def _get_failed_tests(self):
            return [test for test in self.data.keys() if "FAIL" in str(self.data.get(test))]

        def get_failstring(self):
            pass
        
        def get_test(self):
            pass

        class Test:

            def __init__(self, name) -> None:
                self.name
                self.status
                self._limits:self.Limits = None


            def get_limits(self):

                return self._limits    

            @dataclass
            class Limits:
                low: float
                high:float
    
    
    
