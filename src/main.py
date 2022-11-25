


from datetime import datetime
import time
import sys

import configparser
config = configparser.ConfigParser()
config.read('settings\config.ini')

pcf_path = config["Paths"]["pcf"]
input_csv_path = config["Paths"]["input_csv"]

#local modules
from pcf import Pcf
from csvresults import MyCsv

def main():

    pcf = Pcf(pcf_path)
    my_csv = MyCsv(input_csv_path, pcf)


    temp_curr_date = datetime.now()
    print(temp_curr_date)

    last_record = my_csv.get_last_record()

    while temp_curr_date > last_record.date:
        print("waiting for new record...")
        time.sleep(1)
        last_record = my_csv.get_last_record()


    if not last_record.passed: 
        print("fails: \n", last_record.get_failstring())


if __name__ == "__main__":
    main()