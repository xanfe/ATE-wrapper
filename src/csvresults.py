from __future__ import annotations

import pandas as pd
from pandas import DataFrame
import re

from dataclasses import dataclass
from pcf import Pcf

DATE_COLUMN_NAME = '[TIME] TIMESTAMP / RECORD ID'

class Csv:

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
            self.results:Csv = csv
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
                if test_name == test._name:
                    return test
            raise KeyError(test_name)
        
        def __repr__(self) -> str:
            return repr(self.data)
        
        def _get_failed_tests(self) -> list[Test]:
            return [test for test in self.tests if "FAIL" in str(test.data)]

        def get_failstring(self):
            failstring = ""
            for test in self._get_failed_tests():

                failstring += '|ftestres=0,{},{},{},{},{},{},{}\n'. \
                    format(
                        test.fullname,
                        test.meas,
                        test.limits.high,
                        test.limits.low,
                        test.nominal,
                        test.units,
                        test.operator
                        )

            return failstring
        
        class Test:

            def __init__(self, outer:Csv.Record, name:str, data) -> None:
                self._name = name
                self.data = data
                if not isinstance(outer, Csv.Record):
                    raise TypeError(f"exp type: {Csv.Record}, recv type {type(outer)}")
                self.record = outer
                self.metadata:DataFrame = self.record.results.pcf["TEST RESULTS SPECIFICATIONS"].get_spec(self.name)

            @property
            def fullname(self) -> str:
                return re.split(r' \[', self._name)[0]
            
            @property
            def name(self) -> str:
                return re.split(r' HIGH| LOW', self.fullname)[0]

            @property
            def status(self) -> bool:
                return True if 'PASS' in self.data else False
                
            
            @property
            def meas(self):
                if self.type == "DBL":
                    try:
                        return self.record[f'{self.fullname} [MEAS]'].data
                    except KeyError:
                            return int(not self.nominal)
  
                elif self.type == "BOOLEAN":
                    return int(self.status)
                
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
                return self.Limits(self)
            
            @property
            def operator(self) -> str:
                return '<>'

            def __repr__(self) -> str:
                return f'{self.fullname} : {self.data}'
            
            def _get_attr(self, attr_name):
                if attr_name in self.metadata:
                    print(list(self.metadata[attr_name].values))
                    return self.metadata[attr_name].values[0]
                else:
                    raise Exception(f"the metadata for this test does not containt '{attr_name}'")

            
            class Limits:

                def __init__(self, test:Csv.Record.Test) -> None:

                    self.low: float = None
                    self.high:float = None
                    self.test = test
                    self.setup()
                
                def setup(self):

                    if self.test.type == "DBL" and len(self.test.metadata) > 1:
      
                        low_series = self.test.metadata.loc[self.test.metadata['Step ID'].str.contains("LOW")]
                        if "WATER" in low_series['Step ID'].values[0]:
                            print(low_series['Step ID'].values[0])
                        high_series = self.test.metadata.loc[self.test.metadata['Step ID'].str.contains("HIGH")]
                        self.low =  float(low_series["Nominal"] - low_series["Tolerance"])
                        self.high = float(high_series["Nominal"] + high_series["Tolerance"])



                def __repr__(self) -> str:
                    return f'low: {self.low} high: {self.high}'
    
    
    
