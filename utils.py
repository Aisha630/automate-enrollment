
import logging
import colorlog


URL="https://enroll.wisc.edu/my-courses"

TIMEOUT_MAX = 60 * 3 * 1000  # 5 minutes in milliseconds
SCREENSHOTS_DIR = "screenshots"

def init_logging():
    logger = logging.getLogger('enrollment')
    logger.setLevel(logging.DEBUG)

    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s - %(levelname)s - %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
        }
    )
    # console logs. Uncomment this if you do not want console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(f'enrollment.log', mode='w')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    return logger
