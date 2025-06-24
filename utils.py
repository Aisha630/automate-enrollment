
import logging
import colorlog


URL = "https://enroll.wisc.edu/my-courses"

TIMEOUT_MAX = 60 * 3 * 1000  # 3 minutes in milliseconds
SCREENSHOTS_DIR = "screenshots"

SELECTORS = {
    "username": "#j_username",
    "password": "#j_password",
    "login_button": "button[name='_eventId_proceed']",
    "term_dropdown": "#mat-select-value-1 > span",
    "term_option": lambda term: f"mat-option:has-text('{term}')",
    "cart_button": "#categories cse-category-indicator:nth-child(1) button span.left.grow",
    "checkboxes": "input[type='checkbox']",
    "revalidate_btn": "#list cse-category-actions-component button:nth-child(2)",
    "enroll_btn": "#list cse-category-actions-component button:nth-child(3) span.mdc-button__label",
    "dialog": "mat-dialog-container.mdc-dialog--open",
    "enroll_confirm": "Enroll",
    "close_btn": "Close",
    "invalid_appt": "You do not have a valid enrollment appointment at this time.",
    "unsuccessful_enrollment": "mat-icon:has-text('cancel')"
}


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
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    return logger
