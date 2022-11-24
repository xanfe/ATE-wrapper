import pandas as pd
from datetime import datetime

DATE_C_NAME = '[TIME] TIMESTAMP / RECORD ID'

class Record:

    def __init__(self, data:pd.Series) -> None:
        self.data:pd.Series = data
        self.date = data.get(DATE_C_NAME)

    def get_failstring(self):
        print("imprimiendo record")
        print(self.data)



class CsvResults:

    def __init__(self, csv_path) -> None:
        self.results_csv_path = csv_path
        self.df = None
        self._update_df()
    
    def _to_datetime(self):
        self.df[DATE_C_NAME] = pd.to_datetime(self.df[DATE_C_NAME], format='%Y-%m-%d_%H:%M:%S.%f')
    
    def get_last_record(self):
        self._update_df()
        return Record(self.df.iloc[self.df[DATE_C_NAME].argmax()])
    
    def _update_df(self):
        self.df = pd.read_csv(self.results_csv_path, sep=',')
        self._to_datetime()

