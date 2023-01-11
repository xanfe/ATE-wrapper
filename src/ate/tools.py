import configparser
import json
import re
config = configparser.ConfigParser()
config.read('settings\config.ini')

ate_sys_cfg_path = config["Paths"]["ate_system_cfg"]
ate_v = config["AteConfig"]["version"]
p_order = config["AteConfig"]["p_order"]
tdrs_root_path = config["Paths"]["tdrs_root"]

#patterns
serial_num_patterns = config["Patterns"]["serial_number"]
config.read(ate_sys_cfg_path)

#ate_system_cfg
ate_station_id = config["ATE SYSTEM SETTINGS"]["STATION ID"]
ate_system_pnumber = config["ATE SYSTEM SETTINGS"]["SYSTEM PART NUMBER"]



#TDR stands for Test Data Record
#example :TDR_087-00015-02_[KEMX_REX_MFG_1]_[V_0002]_[PO_VERIFY].CSV
def build_tdrs_csv_path():
    path = rf"{tdrs_root_path}\TDR_{ate_system_pnumber}_[{ate_station_id}]_[V_{ate_v}]_[PO_{p_order}].CSV"
    return path


def get_serial_number_patterns():
    patterns = []
    if ',' in serial_num_patterns:
        for pattern in serial_num_patterns.split(','):
            patterns.append(pattern)
        return patterns
    else:
        return [serial_num_patterns]



def get_pattern_matches(patterns, string):

    for pattern in patterns:
        if re.match(pattern, string):
            yield True

        else:
            yield False



