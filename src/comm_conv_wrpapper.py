
from datetime import datetime
import time
import sys
from tkinter import Tk

import configparser
config = configparser.ConfigParser()
config.read('settings\config.ini')

pcf_path = config["Paths"]["pcf"]
input_csv_path = config["Paths"]["input_csv"]

#local modules
from ate.pcf import Pcf
from ate.csvresults import Csv
from ate.testspec import TestSpec
from kemx.grrgen import GRR, generate_grr_savename
from gui.popups import MainApplication


def main():

    pcf = Pcf(pcf_path)
    comm_conv_test_spec = TestSpec("comm_conv", pcf)
    my_csv = Csv(input_csv_path, comm_conv_test_spec)
    # temp_grr = GRR(generate_grr_savename(), comm_conv_test_spec)

    # root = Tk()
    # root.withdraw()
    # gui_app = MainApplication(root)


    temp_curr_date = datetime.now()
    print(temp_curr_date)

    

    # while True:

    #     ask_serial_window = gui_app.ask_serial()

    #     gui_app.wait_window_destroy(ask_serial_window)


    last_record = my_csv.get_last_record()
    while temp_curr_date > last_record.date:
        print("waiting for new record...")
        time.sleep(1)
        last_record = my_csv.get_last_record()
    
    #temp_grr.append_record(last_record)


    if not last_record.passed: 
        print("fails:\n", last_record.get_failstring())


if __name__ == "__main__":
    main()