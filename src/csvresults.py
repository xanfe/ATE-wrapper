from __future__ import annotations
import pandas as pd
from pandas import DataFrame
import re

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
        def passed(self) -> bool:
            try:
                return True if self.data["[RESULT] TEST P/F STATUS"] == 'PASS' else False
            finally:
                self.data = self.data.drop("[RESULT] TEST P/F STATUS")

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
                print("test name: ", test.name)
                print("test type: ", test.type)
                print("test status: ", test.status)
                print("test limits: ", test.limits)
                print("test units: ", test.units)
        
        


        class Test:

            def __init__(self, outer:MyCsv.Record, name:str, data) -> None:
                self._name = name
                self.data = data
                
                if not isinstance(outer, MyCsv.Record):
                    raise TypeError(f"exp type: {MyCsv.Record}, recv type {type(outer)}")
                self.record = outer
                self.metadata:DataFrame = self.record.results.pcf["TEST RESULTS SPECIFICATIONS"].get_rows(self.name)


            @property
            def name(self) -> str:
                return re.split(r' LOW \[| HIGH \[| \[', self._name)[0]

            @property
            def status(self) -> bool:
                return True if 'PASS' in self.data else False
            
            @property
            def type(self) -> str:
                return self._get_attr("Data Type")
            
            @property
            def nominal(self) -> float:
                 return self._get_attr("Nominal")
            
            @property
            def units(self) -> str:
                return self._get_attr("Units")
            
            @property
            def limits(self) -> Limits:
                if self.type == "DBL" and len(self.metadata) > 1:
                    low_series = self.metadata.loc[self.metadata['Step ID'] == self.name + ' LOW']
                    high_series = self.metadata.loc[self.metadata['Step ID'] == self.name + ' HIGH']
                    low_l =  float(low_series["Nominal"] - low_series["Tolerance"])
                    high_l = float(high_series["Nominal"] + high_series["Tolerance"])
                    return self.Limits(low_l, high_l)


            
            def __repr__(self) -> str:
                return f'{self.name} : {self.data}'
            
            def _get_attr(self, attr_name):
                if attr_name in self.metadata:
                    return self.metadata[attr_name].values[0]
                else:
                    raise Exception(f"the metadata for this test does not containt '{attr_name}'")

            
            @dataclass
            class Limits:
                low: float
                high:float

                def __repr__(self) -> str:
                    return f'low: {self.low} high: {self.high}'
    
    
    
