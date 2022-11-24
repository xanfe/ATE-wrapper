

import configparser
from datetime import datetime
import time

#local modles
from pcf import Pcf
from resultscan import CsvResults

def main():

    pcf = Pcf("settings\headers_info.pcf")

    # print(pcf["TEST RESULTS SPECIFICATIONS"])

    results = CsvResults("data\sample\input.csv")

    temp_curr_date = datetime.now()
    print(temp_curr_date)

    last_record = results.get_last_record()

    while temp_curr_date > last_record.date:
        print("aun no hay nada")

        time.sleep(1)
        last_record = results.get_last_record()


    last_record.get_failstring()

    #print("se escribio algo !")

if __name__ == "__main__":
    main()