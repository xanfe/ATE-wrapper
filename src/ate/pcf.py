from __future__ import annotations
from io import StringIO
import pandas as pd
from pandas import DataFrame
import re


class Pcf:
    """The pcf class defines a product config file, the pcf file contains
    used information about the product for an specific part number, the
    most useful information in this file is in the header 
    "TEST RESULTS SPECIFICATIONS" it contains information of each 
    performed test, such as nominal, tolerance, data type, units, etc
    """
    def __init__(self, path:str) -> None:
        """initialices Pcf object

        Parameters
        ----------
        path : str
            reference path to locate pfc file
        """
        self.path = path
        self.sections = []
        self._set_sections()
    
    def __getitem__(self, key) -> Section:
        for section in self.sections:
            if key in section.name:
                return section
        raise KeyError(key)

    def _get_raw_sections(self):
        with open(self.path) as pcf:
            pattern = r'\n,{0,20}\n'
            return re.split(pattern, pcf.read())

    def _set_sections(self):
        for raw_section in self._get_raw_sections():
            name, data = tuple(raw_section.split('\n', 1))
            if "TEST RESULTS SPECIFICATIONS" in name:
                self.sections.append(self.TestSpecSection(name.rstrip(','), data))
                return
            elif "TEST STIMULUS SPECIFICATIONS" in name:
                pass #TODO
            elif "CONFIGURATION" in name:
                pass #TODO
            
        raise Exception("unhandled section name")
    
    class Section():
        """
        a section class defines the contents of a header in the pcf file
        """
        def __init__(self, name, str_data) -> None:
            self.name:str = name
            self.df = pd.read_csv(StringIO(str_data), sep=',')
            self.column_names = self.df.columns
            self.records = self.df.to_records()
        
        def __repr__(self) -> str:
            return str(self.df.head())
        
        
        

    class TestSpecSection(Section):
        def __init__(self, name, data) -> None:
            super().__init__(name, data)
            self.test_specs = None
            self.test_names = []
            self.low_limits = []
            self.high_limits = []
            self.setup_spec()
        
        def get(self, step_name):
            return self.df.loc[self.df['Step ID'] == step_name]
            
        def setup_spec(self) -> list[SingleTestSpec]:
            self.test_specs = [self.SingleTestSpec(self.get(test_name), test_name) for test_name in self.df["Step ID"]]
            for test_spec in self.test_specs:
                self.test_names.append(test_spec.name)
                self.low_limits.append(test_spec.low_limit)
                self.high_limits.append(test_spec.high_limit)
            tup = ((test_spec.name, test_spec.low_limit, test_spec.high_limit) for test_spec in self.test_specs)
            print(tup)
        
        
        def __getitem__(self, test_name):
            for test_spec in self.test_specs:
                if test_spec.name == test_name:
                    return test_spec
            return None
        

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



