from __future__ import annotations
from io import StringIO
import pandas as pd
import re


class Pcf:
    """

    The pcf class defines a process control file, the pcf file contains
    used information in the process for an specific part number, the
    most useful information in this file is in the header 
    "TEST RESULTS SPECIFICATIONS" it contains information of each 
    performed test, such as nominal, tolerance, data type, units, etc
    
    """
    def __init__(self, path) -> None:
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
            name_w_data = raw_section.split('\n', 1)
            self.sections.append(self.Section(name_w_data[0], name_w_data[1]))
    
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
        
        
        def get(self, step_name):
            return self.df.loc[self.df['Step ID'] == step_name]


