# ATE-Wrapper

this python project consists in a handler for an external test software, where the main task is to extrat the 
generated results of this external software.

the results are recorded in csv rows when a PCB test finishes.

the column names of the csv file are related with the `settings/headers_info.pcv` file, that file contains all
extra info of all column names/test names such as, limits, nominal values, units, etc