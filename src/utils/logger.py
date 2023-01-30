import logging
from logging import _Level
from logging.handlers import RotatingFileHandler
from datetime import datetime
from os.path import join as join




class Logger(logging.Logger):

    def __init__(self, name: str, save_path: str = ".", rotate = True) -> None:
        """
        Create a new file and streaming logger.

        Debug mode is initially set True when first generated.
        Default logger name is "application_logger".

        Args:
            name (str): TODO
            save_path (str, optional): The absolute path to save log files to. Defaults to ".".
            rotate (bool, optional): TODO

        Returns:
            logger.Logger: A logging object with streaming and file handlers.
        """
        super().__init__(name)

        try:

            # Console handlers.
            ch = logging.StreamHandler()


            # Setup single file handler or rotating handler to 25MB cap and 20 files.
            if rotate:
                f_name = f"{name}.log"
                fh = RotatingFileHandler(
                    filename=join(save_path, f_name), maxBytes=10_000_000, backupCount=20
                )
            else:
                f_name = f"{name}_{datetime.now()}.log"
                fh = logging.FileHandler(filename=join(save_path, f_name))
            

            ch.setLevel(logging.DEBUG)
            fh.setLevel(logging.DEBUG)

            # Console and file formatters.
            c_formatter = logging.Formatter("%(message)s")
            f_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
            )

            # Add formatters to ch.
            ch.setFormatter(c_formatter)
            fh.setFormatter(f_formatter)

            # Add ch to logger.
            self.addHandler(ch)
            self.addHandler(fh)
        except:
            self.error(f"An Exception occurred when creating custom logger object")
    
    def set_debug(self, lvl):
        """
        Set the logging level of the logger between INFO and DEBUG.

        Args:
            logger (logging.logger): A logging object instance.
            lvl (bool): True or False to enable or disable debug mode respectively.
        """
        try:
            if lvl:
                self.setLevel(logging.DEBUG)
            else:
                self.setLevel(logging.INFO)
            self.debug(f"Logging debug set to: {lvl}")
        except Exception as e:
            self.error(f"An Exception occurred when setting logging debug level: {e}")



