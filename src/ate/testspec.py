from pcf import Pcf
from pandas import DataFrame

import configparser
config = configparser.ConfigParser()
config.read('settings\config.ini')

pcf_path = config["Paths"]["pcf"]
input_csv_path = config["Paths"]["input_csv"]

class TestSpec:
    def __init__(self, name, process_control_file_path:str) -> None:
        self.name = name
        self.pcf_path = process_control_file_path
        self.pcf = Pcf(self.pcf_path)

    #specifications for each test. name, limits, units, etc
    @property
    def specs(self) -> Pcf.Section:
        return self.pcf["TEST RESULTS SPECIFICATIONS"]
    
    @property
    def test_names(self) -> list[str]:
        return [test_name for test_name in self.specs.df["Step ID"]]

    @property
    def low_limits(self):
        return self.__get_limit("LOW")
    
    @property
    def high_limits(self):
        return self.__get_limit("HIGH")
    
    def __get_limit(self, limit_type):
        limits = []
        for test_name in self.test_names:
            test_spec = self.specs.get(test_name)
            if test_spec["Spec Type"].values[0] == "NUMERIC OVER":
                if limit_type == "HIGH":
                    limit = float('inf')
                elif limit_type == "LOW":
                    limit = test_spec["Nominal"].values[0]
                else:
                    pass #TODO
            elif test_spec["Spec Type"].values[0] == "NUMERIC UNDER":
                if limit_type == "HIGH":
                    limit = test_spec["Nominal"].values[0]
                elif limit_type == "LOW":
                    limit = float('-inf')
                else:
                    pass #TODO
            elif test_spec["Spec Type"].values[0] == "% TOLERANCE":
                nominal = test_spec["Nominal"].values[0]
                if limit_type == "HIGH":
                    limit = nominal + nominal * test_spec["Tolerance"].fillna(0).values[0]
                elif limit_type == "LOW":
                    limit = nominal - nominal * test_spec["Tolerance"].fillna(0).values[0]
                else:
                    pass #TODO
            else:
                if limit_type == "HIGH":
                    limit = test_spec["Nominal"].values[0] + test_spec["Tolerance"].fillna(0).values[0]
                elif limit_type == "LOW":
                    limit = test_spec["Nominal"].values[0] - test_spec["Tolerance"].fillna(0).values[0]
                else:
                    pass #TODO
            limits.append(limit)
        return limits

    class SingleTestData:
        def __init__(self, name) -> None:
            self.name = name



