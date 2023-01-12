"""
This module provides the Pcf class, which defines a product config file (PCF) object.
A PCF file contains information about a product for a specific part number,
with the most useful information in the header "TEST RESULTS SPECIFICATIONS", 
which contains information of each performed test, such as nominal, tolerance, data type, units, etc.
The Pcf class provides a way to access the data in the PCF file, by reading the file and parsing it into sections.
These sections are represented by Section objects, with the most important one being the TestSpecSection that
represents the "TEST RESULTS SPECIFICATIONS" header.
"""

from __future__ import annotations
from io import StringIO
import pandas as pd
from pandas import DataFrame
import re


class Pcf:
    """The Pcf class provides an interface for reading and parsing Product Configuration Files (PCF). 
    It allows for easy access to the information contained in the file, such as test results and specifications.
    A PCF file contains information about a product for a specific part number, with the most useful information in the
    header "TEST RESULTS SPECIFICATIONS", which contains information of each performed test, such as nominal, tolerance,
    data type, units, etc.
    
    Attributes
    ----------
    path : str
        The relative or absolute path of the PCF file.
    sections : list[Section]
        A list containing Section objects, representing different sections of the PCF file.
        Currently, only the "TEST RESULTS SPECIFICATIONS" section is supported and is represented by an instance of the
        TestSpecSection class.
    
    Methods
    -------
    __getitem__(self, header_name: str) -> Section
        Retrieves a Section object by its header name.
    """
    def __init__(self, path: str) -> None:
        """constructor for Pcf class

        Parameters
        ----------
        path : str
            relative or abs path of the pcf file
        """
        self.path = path
        self.sections: list[Pcf.Section] = []
        self._set_sections()

    def __getitem__(self, header_name: str) -> Section:
        """Retrieves a Section object by a given header name

        Parameters
        ----------
        header_name : str
            name of the section, header for a set of data

        Returns
        -------
        Section
            the section that matches the given heaer name

        Raises
        ------
        KeyError
            if header_name doesn't match any of the available
            section header names, raises exception
        """
        for section in self.sections:
            if header_name in section.name:
                return section
        raise KeyError(header_name)

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
                # TODO
                pass
            elif "CONFIGURATION" in name:
                # TODO
                pass
        raise Exception("unhandled section name")

    class Section():
        """base section class to define the contents of a header in a pcf file

        Attributes
        ----------

        name : str
            name of the section, see diferent names at :class:`Pcf` class
        df : Dataframe
            Dataframe from raw csv string in `data` parameter


        """
        def __init__(self, name: str, data: str) -> None:
            """constructor dunder method to create an instance of `Section`
            Class

            Parameters
            ----------
            name : str
                name of the section, see diferent names at :class:`Pcf` class
            data : str
                raw section data in csv format
            """
            self.name = name
            self.df = pd.read_csv(StringIO(data), sep=',')
            # self.column_names = self.df.columns
            # self.records = self.df.to_records()

        def __repr__(self) -> str:
            return str(self.df.head())

    class TestSpecSection(Section):
        """Defines a class

        Parameters
        ----------
        name : str
            _description_
        data : str
            _description_
        """
        def __init__(self, name: str, data: str) -> None:

            super().__init__(name, data)
            self.test_specs = None
            self.test_names = []
            self.low_limits = []
            self.high_limits = []
            self._setup_spec()
        
        def get(self, step_name: str):
            """searches for the specific given test name and returns
            the test data as a dataframe

            Args:
                step_name (str): name of the specific single test

            Returns:
                pandas.Dataframe
            """
            return self.df.loc[self.df['Step ID'] == step_name]
            
        def _setup_spec(self) -> list[SingleTestSpec]:
            self.test_specs = [self.SingleTestSpec(self.get(test_name), test_name) for test_name in self.df["Step ID"]]
            for test_spec in self.test_specs:
                self.test_names.append(test_spec.name)
                self.low_limits.append(test_spec.low_limit)
                self.high_limits.append(test_spec.high_limit)
            # tup = ((test_spec.name, test_spec.low_limit, test_spec.high_limit) for test_spec in self.test_specs)
            # print(tup)

        def __getitem__(self, test_name: str) -> SingleTestSpec:
            """Retrieve a test spec object by a given test name

            Parameters
            ----------
            test_name : str
                name of the test to be retrieved

            Returns
            -------
            SingleTestSpec
                the test spec that matched the test_name
            """
            for test_spec in self.test_specs:
                if test_spec.name == test_name:
                    return test_spec
            return None

        class SingleTestSpec:
            """Defines an object to represent a specific single test metadata

            Attributes
            ----------
            spec : DataFrame
                asd

            name : str
                name of the test

            Properties
            ----------


            """
            def __init__(self, spec: DataFrame, test_name: str) -> None:
                """_summary_

                Parameters
                ----------
                spec : DataFrame
                    contents the test metadata in form of a pandas dataframe
                test_name : str
                    name of the test
                """
                self.name = test_name
                self.spec = spec
                self._low_limit = None
                self._high_limit = None
                self._setup_limits()

            @property
            def low_limit(self) -> float:
                """low limit to be evaluated on test measurement

                Returns
                -------
                float
                    depending on the type of test and tolerance,
                    calculates low limit
                """
                return self._low_limit

            @property
            def high_limit(self) -> float:
                """high limit to be evaluated on test measurement

                Returns
                -------
                float
                    depending on the type of test and tolerance,
                    calculates high limit
                """
                return self._high_limit

            @property
            def data_type(self) -> str:
                """ data type refers to the test measurement type

                Returns
                -------
                str
                    any of the following strings:
                    DLB,
                    STRING,
                    BOOLEAN,
                    CORRELATION DBL
                """
                return self.spec["Data Type"].values[0]

            @property
            def type(self) -> str:
                """refers to the type of the test, not the type of mesuremnt
                like the 'data_type' property

                Returns
                -------
                str
                    depending on `spec` attribute returns any
                    of the following strings:
                    NUMERIC OVER,
                    NUMERIC UNDER,
                    % TOLERANCE,
                    ABS TOLERANCE,
                    STRING,
                    BOOLEAN

                """
                return self.spec["Spec Type"].values[0]

            @property
            def nominal(self):
                """expected value, ideal value for the test

                Returns
                -------
                any
                    the expected value could from a float, bool or string
                """
                return self.spec["Nominal"].values[0]
            
            @property
            def units(self) -> str:
                """ measurements units of the test result

                Returns
                -------
                str
                    extracts test units from `spec`, could be "VCD" or ""
                """
                return self.spec["Units"].values[0]

            @property
            def tolerance(self) -> float:
                """tolerance to be applied to DBL type measurements

                Returns
                -------
                float
                    relative float value or perc value depending
                    on the test type
                """
                return self.spec["Tolerance"].fillna(0).values[0]

            def _setup_limits(self): 
                if self.type == "NUMERIC OVER":
                    self._high_limit = float('inf')
                    self._low_limit = self.nominal

                elif self.type == "NUMERIC UNDER":
                    self._high_limit = self.nominal
                    self._low_limit = float('-inf')

                elif self.type == "% TOLERANCE":
                    self._high_limit = self.nominal + self.nominal * self.tolerance
                    self._low_limit = self.nominal - self.nominal * self.tolerance
                else:
                    self._high_limit = self.nominal + self.tolerance
                    self._low_limit = self.nominal - self.tolerance



