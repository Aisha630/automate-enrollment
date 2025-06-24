from playwright.sync_api import sync_playwright, Page
from dataclasses import dataclass, field
from typing import Optional
import time
import os
from dotenv import load_dotenv
from utils import *
from pathlib import Path

logger = init_logging()


@dataclass
class Enrollment:
    semester: str = field(default="Fall 2025")
    page: Optional[Page] = field(default=None, init=False)
    profile_dir: str = field(default="./chrome_profile", init=False)
    try_number: int = field(default=0, init=False)

    def __post_init__(self):
        load_dotenv()

        if not os.getenv("NET_ID") or not os.getenv("PASSWORD"):
            logger.error("Environment variables NET_ID and PASSWORD must be set.")
            raise ValueError("Missing credentials in .env")

        if not self.semester:
            logger.error("Semester must be specified.")
            raise ValueError("Missing semester")

        Path(self.profile_dir).mkdir(exist_ok=True)
        Path(SCREENSHOTS_DIR).mkdir(exist_ok=True)

    def run(self):
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                self.profile_dir,
                headless=False
            )
            self.page = browser.new_page()
            self.page.set_default_timeout(TIMEOUT_MAX)

            self.navigate_to_enrollment()
            self.enroll()

    def navigate_to_enrollment(self):
        self.page.goto(URL)
        self.page.reload(wait_until="networkidle")

        if self.page.is_visible(SELECTORS["username"]):
            logger.info(f"Logging in as {os.getenv('NET_ID')}")
            self.page.fill(SELECTORS["username"], os.getenv("NET_ID"))
            self.page.fill(SELECTORS["password"], os.getenv("PASSWORD"))
            self.page.click(SELECTORS["login_button"])

    def select_semester(self):
        try:
            self.page.wait_for_selector(SELECTORS["term_dropdown"])
            self.page.click(SELECTORS["term_dropdown"])
            self.page.click(SELECTORS["term_option"](self.semester))
            logger.info(f"Selected semester: {self.semester}")
        except Exception as e:
            logger.error(f"Failed to select semester: {self.semester}")
            logger.exception(e)
            raise

    def open_cart(self):
        self.page.wait_for_selector(SELECTORS["cart_button"])
        self.page.click(SELECTORS["cart_button"])
        logger.info("Opened course cart")

    def attempt_enrollment(self) -> bool:
        self.try_number += 1
        logger.debug(f"Attempt #{self.try_number} to enroll")

        # Check all checkboxes
        self.page.wait_for_selector(SELECTORS["checkboxes"])
        checkboxes = self.page.query_selector_all(SELECTORS["checkboxes"])

        if not checkboxes:
            logger.error("No courses in cart or checkboxes not found.")
            return False

        for checkbox in checkboxes:
            if not checkbox.is_checked():
                checkbox.click()

        # Revalidate cart
        logger.info("Revalidating cart...")
        self.page.click(SELECTORS["revalidate_btn"])

        # Enroll
        logger.info("Clicking 'Enroll' button...")
        self.page.click(SELECTORS["enroll_btn"])

        # Wait for and interact with the enrollment dialog
        dialog = self.page.locator(SELECTORS["dialog"])
        dialog.get_by_text(SELECTORS["enroll_confirm"], exact=True).click()

        logger.info("Waiting for confirmation...")
        close_btn = dialog.get_by_text(SELECTORS["close_btn"], exact=True)
        close_btn.wait_for(state="visible")

        invalid_appt_text = dialog.get_by_text(SELECTORS["invalid_appt"], exact=True)
        cancel_icon = dialog.locator(SELECTORS["unsuccessful_enrollment"])

        if invalid_appt_text.is_visible():
            logger.warning("Invalid appointment. Will retry.")
            screenshot_path = Path(SCREENSHOTS_DIR) / \
                f"invalid_appt_{self.try_number}_{int(time.time())}.png"
            self.page.screenshot(path=screenshot_path)
            close_btn.click()
            return False
        elif cancel_icon.is_visible():
            logger.warning(
                "One or more course enrollment unsuccessful due to reasons other than invalid appointment.")
            screenshot_path = Path(SCREENSHOTS_DIR) / \
                f"failed_attempt_{self.try_number}_{int(time.time())}.png"
            self.page.screenshot(path=screenshot_path)
            exit(0)

        logger.info("All course enrollments successful!")
        success_path = Path(SCREENSHOTS_DIR) / \
            f"complete_success_{self.try_number}_{int(time.time())}.png"
        self.page.screenshot(path=success_path)
        close_btn.click()
        return True

    def enroll(self):
        self.select_semester()
        self.open_cart()

        while True:
            if self.attempt_enrollment():
                return
            logger.info("\nRetrying...")


def main():
    Enrollment().run()


if __name__ == "__main__":
    main()
