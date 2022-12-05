from __future__ import annotations

from pcf import Pcf
from pandas import DataFrame

import configparser
config = configparser.ConfigParser()
config.read('settings\config.ini')

pcf_path = config["Paths"]["pcf"]
input_csv_path = config["Paths"]["input_csv"]

class TestSpec:
    def __init__(self, name:str, process_control_file_obj:Pcf) -> None:
        self.name = name
        self.pcf = process_control_file_obj

    @property
    def specs(self) -> Pcf.Section:
        """
        specifications for each test name, such as limits, nominal, units, etc
        """
        return self.pcf["TEST RESULTS SPECIFICATIONS"]
    
    @property
    def test_specs(self) -> list[SingleTestSpec]:
        return [self.SingleTestSpec(self.specs.get(test_name), test_name) for test_name in self.specs.df["Step ID"]]
    
    @property
    def test_names(self) -> list[str]:
        return [test_spec.name for test_spec in self.test_specs]

    @property
    def low_limits(self) -> list[float]:
        return [test_spec.low_limit for test_spec in self.test_specs]
    
    @property
    def high_limits(self) -> list[float]:
        return [test_spec.high_limit for test_spec in self.test_specs]
    
    def get_single(self, test_name):
        for test_spec in self.test_specs:
            if test_spec.name == test_name:
                return test_spec
        raise(KeyError)
    

    class SingleTestSpec:
        def __init__(self, spec:DataFrame, test_name:str) -> None:
            self.name = test_name
            self.spec = spec
            self.low_limit = None
            self.high_limit = None
            self.setup_limits()
        
        @property
        def data_type(self):
            return self.spec["Data Type"].values[0]
        
        @property
        def type(self):
            return self.spec["Spec Type"].values[0]
        
        @property
        def nominal(self):
            return self.spec["Nominal"].values[0]
        
        @property
        def units(self):
            return self.spec["Units"].values[0]
        
        @property
        def tolerance(self):
            return self.spec["Tolerance"].fillna(0).values[0]

        

        def setup_limits(self):
            
            if self.type == "NUMERIC OVER":
                self.high_limit = float('inf')
                self.low_limit = self.nominal

            elif self.type == "NUMERIC UNDER":
                self.high_limit = self.nominal
                self.low_limit = float('-inf')

            elif self.type == "% TOLERANCE":
                self.high_limit = self.nominal + self.nominal * self.tolerance
                self.low_limit = self.nominal - self.nominal * self.tolerance
            else:
                self.high_limit = self.nominal + self.tolerance
                self.low_limit = self.nominal - self.tolerance


   
