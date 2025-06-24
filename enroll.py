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
            logger.error(
                "Environment variables NET_ID and PASSWORD must be set.")
            return
        if not self.semester.strip():
            logger.error("Semester must be specified.")
            return

        os.makedirs(self.profile_dir, exist_ok=True)
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

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
        if self.page.is_visible("#j_username"):
            logger.info(f"Logging in with NET_ID: {os.getenv('NET_ID')}")
            self.page.fill("input[id='j_username']", os.getenv("NET_ID"))
            self.page.fill("input[id='j_password']", os.getenv("PASSWORD"))
            self.page.click("button[name='_eventId_proceed']")

    def enroll(self):
        """
        Enroll in the specified semester.
        """
        if not self.semester:
            logger.error(
                "Semester not set. Please set the semester before enrolling.")
            return

        # Select the correct term from the drop down before selecting cart
        try:
            self.page.wait_for_selector("#mat-select-value-1 > span")
            self.page.click("#mat-select-value-1 > span")
            self.page.click(f"mat-option:has-text('{self.semester}')")
        except Exception as e:
            logger.error(
                f"Failed to select the semester '{
                    self.semester}'. Please ensure it is available in the dropdown.")
            logger.exception(e)
            return

        # Select the cart
        self.page.wait_for_selector(
            "#categories > section > section > cse-category-indicator:nth-child(1) > button > span.left.grow")
        self.page.click(
            "#categories > section > section > cse-category-indicator:nth-child(1) > button > span.left.grow")

        not_successful = True
        while not_successful:

            self.try_number += 1
            logger.debug(
                f"Attempt {self.try_number} to enroll in {self.semester}")

            # Check all courses in cart
            self.page.wait_for_selector("input[type='checkbox']")
            checkboxes = self.page.query_selector_all("input[type='checkbox']")
            if not checkboxes:
                logger.error(
                    "No checkboxes found in the cart. Please ensure the page is loaded correctly or if you have something in the cart.")
                return
            for checkbox in checkboxes:
                if not checkbox.is_checked():
                    checkbox.click()

            # Validate the cart using 'Revalidate' button
            logger.info("Revalidating cart...")
            self.page.wait_for_selector(
                "#list > section > section > cse-category-actions-component > div > div > button:nth-child(2)")
            self.page.click(
                "#list > section > section > cse-category-actions-component > div > div > button:nth-child(2)")

            # Click on 'Enroll' button
            logger.info("Clicking on 'Enroll' button...")
            self.page.wait_for_selector(
                "#list > section > section > cse-category-actions-component > div > div > button:nth-child(3) > span.mdc-button__label")
            self.page.click(
                "#list > section > section > cse-category-actions-component > div > div > button:nth-child(3) > span.mdc-button__label")

            # Wait for the popup to load and click on 'Enroll' button on the popup
            logger.info("Waiting for 'Enroll' button in the popup...")
            dialog = self.page.locator("mat-dialog-container.mdc-dialog--open")
            dialog.get_by_text("Enroll", exact=True).click()

            logger.info("Enrollment in progress...")

            # Wait for 'Close' button to appear
            close_btn = dialog.get_by_text("Close", exact=True)
            close_btn.wait_for(state="visible")

            invalid_appt = dialog.get_by_text(
                "You do not have a valid enrollment appointment at this time.").first

            if invalid_appt.is_visible():
                logger.warning(
                    "You do not have a valid enrollment appointment at this time. Retrying...")
            else:
                not_successful = False
                logger.info("Enrollment successful!")

            self.page.screenshot(path=Path(
                SCREENSHOTS_DIR) / f"enrollment_success_{self.try_number}_{time.time()}.png")

            # Click on 'Close' button to close the self.page
            close_btn.click()
            logger.info("Closed the enrollment dialog.")


def main():
    Enrollment().run()


if __name__ == "__main__":
    main()
