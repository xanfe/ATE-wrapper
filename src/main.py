

import configparser
from datetime import datetime
import time
import sys

#local modules
from pcf import Pcf
from csvresults import MyCsv

def main():

    pcf = Pcf("settings\headers_info.pcf")
    my_csv = MyCsv("data\sample\input.csv", pcf)


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