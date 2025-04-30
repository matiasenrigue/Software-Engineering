import logging
import sys
import os

def setup_logging(default_level=logging.INFO):
    """
    Configures logging for the application.
    This function sets up a stream handler (to output to console) with a specified format.
    """
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(default_level)

    # If handlers are already configured, you can skip configuration
    if logger.hasHandlers():
        return

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(default_level)

    # Create formatter and add it to the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(console_handler)

    # Optionally, set up a file handler if you want logs written to file
    log_file = os.path.join(os.getcwd(), "app.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(default_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

