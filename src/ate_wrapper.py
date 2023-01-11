from datetime import datetime
import time
import sys
from tkinter import Tk
import ast
import clr

import configparser
config = configparser.ConfigParser()
config.read('settings\config.ini')



#process variables
local_pnumber = config["Process"]["part_number"]
station_name = config["Process"]["station_name"]
p_oder = config["AteConfig"]["p_order"]


#Traceability options
backcheck_serial_enabled = config["TraceabilityOptions"]["backcheck_serial"]
validate_partnumber_enabled = config["TraceabilityOptions"]["validate_partnumber"]
insert_process_enabled = config["TraceabilityOptions"]["insert_process_data"]
only_insert_pass = config["TraceabilityOptions"]["only_insert_pass"]

#paths
firmware_path = config["Paths"]["firmware"]
pcf_path = config["Paths"]["pcf"]
ate_wd = config["Paths"]["ate_software_wd"]
newtonsoftjson_path = config["Paths"]["newtonsoft_json_dll"]
wsconnector_path = config["Paths"]["ws_connector_dll"]







clr.AddReference(newtonsoftjson_path)
clr.AddReference(wsconnector_path)
from WSConnector import Connector

#local modules
from ate.pcf import Pcf
from ate.tdr import TdrsCsv
from ate.tools import *
from gui.popups import MainApplication
from automation.programhandler import ProgramHandler
#from kemx.grrgen import GRR, generate_grr_savename
from gui.popups import MainApplication
from kemx.webservices import WebServices2

START_TEST_BTN_POS = ast.literal_eval(config["ScreenCords"]["start_test_btn"])
NEW_ORDER_BTN_POS = ast.literal_eval(config["ScreenCords"]["new_order_btn"])
BROWSE_FW_BTN_POS = ast.literal_eval(config["ScreenCords"]["browse_fw_btn"]) # position for brose firmware path button


"""
numero de parte: 704-00306-20-001 F
serial: 2208F0110020
exe: 087-00015-02-001
firmware path: C:\AlphaManufacturingTest\ATE_Software\087-00015-20\-000\Firmware Files\ccm_v0.00.0M.s19
serial with flow: 2250F7300009

"""
def setup_ate_sequence(handler : ProgramHandler):
    handler.click(NEW_ORDER_BTN_POS)
    handler.type_and_return(p_oder)
    time.sleep(0.5)
    handler.type_and_return(local_pnumber)
    time.sleep(1.5)
    handler.click(BROWSE_FW_BTN_POS)
    time.sleep(0.8)
    handler.type_and_return(firmware_path)
    time.sleep(0.2)


def main():

    root = Tk()
    root.withdraw()
    gui_app = MainApplication(root)

    ate_handler = ProgramHandler("087-00015-02-001", ate_wd)

    ws_connenction = Connector()

    tdrs_csv_path = build_tdrs_csv_path()

    pcf = Pcf(pcf_path)

    tdrs_csv = TdrsCsv(tdrs_csv_path, pcf["[TEST RESULTS SPECIFICATIONS]"])



    ate_handler.open()
    time.sleep(27) #TODO: replace with virtual visual timer for the operator to know he must wait for the test sequence to be ready



    #TODO:when part number fixed in test sequence, uncomment and correctly implement serial ask
    #temporal comment,the serial number should ideally  be asked here to retrieve part_number from web server
    #but at this point 1/6/2023, this doesnt match the secuence so ini part number will be used
    # ask_serial_wd = gui_app.ask_serial()
    # gui_app.wait_window_destroy(ask_serial_wd)


    ask_serial_wd = gui_app.ask_serial()
    gui_app.wait_window_destroy(ask_serial_wd)

    setup_ate_sequence(ate_handler)


    total_uuts = 0 #counts each unit that has been tested


    def valid_serial_number(serial):

        serial_number_patterns = get_serial_number_patterns()
        serial_pattern_matches = get_pattern_matches(serial_number_patterns, serial)

        if not all(serial_pattern_matches):
            msg_window = gui_app.message(f"FORMATO DE SERIAL INVALIDO:\n patrones: {serial_number_patterns}", "orange")
            gui_app.wait_window_destroy(msg_window)
            return False
        else:
                if validate_partnumber_enabled == 'yes':

                    pnum_ref = ""
                    webservices_pnumber, pnum_ref = ws_connenction.CIMP_PartNumberRef(serial,1, pnum_ref)

                    if local_pnumber.replace(' ', '+') != webservices_pnumber:
                        msg_window = gui_app.message(f"NUMERO DE PARTE INESPERADO: \n    local (.ini): {local_pnumber} \n web server: {webservices_pnumber}", "orange")
                        gui_app.wait_window_destroy(msg_window)

                        #----------------------------------------------------------------------
                        #aqui puede ir mensaje al operador para retirar la pieza del fixture
                        msg_window = gui_app.message("RETIRE LA PIEZA Y\n TOME UNA NUEVA", "blue")
                        gui_app.wait_window_destroy(msg_window)
                        #----------------------------------------------------------------------
                        return False
                        
                    else:
                        return True
                else:
                    return True

    try:
        while True:


            if not ate_handler.opened:
                pass #TODO: implement logic to repopen ate-software

            
            
            if total_uuts > 0:
                ask_serial_wd = gui_app.ask_serial()
                gui_app.wait_window_destroy(ask_serial_wd)

            ate_handler.click(START_TEST_BTN_POS)
            time.sleep(0.3)
            ate_handler.type_and_return(gui_app.serial)


            if not valid_serial_number(gui_app.serial):
                continue
            
                    

            #se hace el backcheck de la pieza
            if backcheck_serial_enabled == 'yes':
                resp = ws_connenction.BackCheck_Serial(gui_app.serial, station_name)
            else:
                resp = f"1|OK: Unidad correcta: SN: {gui_app.serial}"
            


            if not resp == f"1|OK: Unidad correcta: SN: {gui_app.serial}":


                msg_window = gui_app.message("FALLA DE BACKCHECK:\n" + resp, "orange")
                gui_app.wait_window_destroy(msg_window)

                #----------------------------------------------------------------------
                #aqui puede ir mensaje al operador para retirar la pieza del fixture
                msg_window = gui_app.message("RETIRE LA PIEZA Y\n TOME UNA NUEVA", "blue")
                gui_app.wait_window_destroy(msg_window)
                #----------------------------------------------------------------------

                #la palabra reservada continue, descarta el ciclo actual del loop, y continua con el siguiente
                #ciclo desde el principio
                continue

            msg_window = gui_app.message("INSERTE LA PIEZA Y \nBAJE EN EL FIXTURE", "blue")
            gui_app.wait_window_destroy(msg_window)

            temp_curr_date = datetime.now()
            test_start_time = str(temp_curr_date)[:19]
            print("temp_curr_date: ", temp_curr_date)

            ate_handler.busy = True


            last_record = tdrs_csv.get_last_record()
            print("last record date: ", last_record.date)


            while temp_curr_date > last_record.date:
                print("waiting for new record.....................................................")
                time.sleep(1)

                last_record = tdrs_csv.get_last_record()
                print("init timestamp: ", test_start_time)
                print("last record date: ", last_record.date)
            

            if not last_record.serial == gui_app.serial:
                err_msg_window = gui_app.message(f"SERIAL DE ARCHIVO CSV NO \n CORRESPONDE AL ESCANEADO: csv: {last_record.serial} \n escaneado: {gui_app.serial}")
                gui_app.wait_window_destroy(err_msg_window)
                continue
                

            
            test_end_time = str(datetime.now())[:19]
            ate_handler.busy = False

            if last_record.status:
                msg_window = gui_app.message("TEST FUNCTIONAL PASSED", "green", 40)
                failstring = ""
            else:
                msg_window = gui_app.message("TEST FUNCTIONAL FAILED", "red", 40)
                failstring = last_record.build_failstring()
            
            gui_app.wait_window_destroy(msg_window)
            

            def insert_process_data():
                return ws_connenction.InsertProcessDataWithFails(gui_app.serial,
                                                            station_name,
                                                            "TEST FINAL FUNCTIONAL",
                                                            test_start_time,
                                                            test_end_time,
                                                            last_record.status,
                                                            failstring,
                                                            "employee")
            

            print("data to insert:")
            print("{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
                gui_app.serial,
                station_name,
                "FUNCTIONAL TEST>TOP",
                test_start_time,
                test_end_time,
                last_record.status,
                failstring,
                "employee"
            ))

            if insert_process_enabled == 'yes':
                if only_insert_pass == 'yes':
                    if last_record.status == 1:
                        reply = insert_process_data()
                    else:
                        reply = "Ok"
                else:
                    reply = insert_process_data()
            else:
                reply = "Ok"
            

            if not "Ok" in reply:

                #TODO: agregar reintentos si falla al subir a traceabilidad
                msg_window = gui_app.message("FALLA AL SUBIR A TRACEABILIDAD: \n"+ reply, "orange")
                gui_app.wait_window_destroy(msg_window)



            #-----------------------------------------------------------


            #TODO: agregar generacion de GRR's en tiempo real

            #-----------------------------------------------------------




            #----------------------------------------------------------------------
            #aqui puede ir mensaje al operador para retirar la pieza del fixture
            msg_window = gui_app.message("RETIRE LA PIEZA Y\n TOME UNA NUEVA", "blue")
            gui_app.wait_window_destroy(msg_window)
            #----------------------------------------------------------------------
            total_uuts += 1
    
    finally:
        #cleanup
        if not ate_handler.busy:
            ate_handler.close()

    root.destroy()
    root.mainloop()





if __name__ == "__main__":
    main()