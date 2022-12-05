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
    def low_limits(self):
        return [test_spec.low_limit for test_spec in self.test_specs]
    
    @property
    def high_limits(self):
        return [test_spec.high_limit for test_spec in self.test_specs]
    

    class SingleTestSpec:
        def __init__(self, spec:DataFrame, test_name:str) -> None:
            self.name = test_name
            self.spec = spec
            self.low_limit = None
            self.high_limit = None
            self.setup_limits()
        

        def setup_limits(self):
            
            if self.spec["Spec Type"].values[0] == "NUMERIC OVER":
                self.high_limit = float('inf')
                self.low_limit = self.spec["Nominal"].values[0]

            elif self.spec["Spec Type"].values[0] == "NUMERIC UNDER":
                self.high_limit = self.spec["Nominal"].values[0]
                self.low_limit = float('-inf')

            elif self.spec["Spec Type"].values[0] == "% TOLERANCE":
                nominal = self.spec["Nominal"].values[0]
                self.high_limit = nominal + nominal * self.spec["Tolerance"].fillna(0).values[0]
                self.low_limit = nominal - nominal * self.spec["Tolerance"].fillna(0).values[0]
            else:
                self.high_limit = self.spec["Nominal"].values[0] + self.spec["Tolerance"].fillna(0).values[0]
                self.low_limit = self.spec["Nominal"].values[0] - self.spec["Tolerance"].fillna(0).values[0]


   
