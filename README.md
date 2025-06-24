# UW Madison Course Enrollment Automation

An automated tool for enrolling in courses at the University of Wisconsin-Madison using Playwright web automation.

## Overview

This project automates the process of enrolling in courses through the UW Madison enrollment system. It uses a persistent Chrome browser profile to maintain login sessions and automatically attempts to enroll in all courses in your cart for a specified semester.

## Prerequisites

- Python 3.13 or higher
- Chrome browser installed
- Valid UW Madison NetID and password
- Courses already added to your enrollment cart

## Installation

1. Clone or download this repository
2. Install dependencies using uv (recommended) or pip:

```bash
# Using uv
uv sync
```

3. Install Playwright browsers:

```bash
playwright install chromium
```

## Configuration

1. Create a `.env` file in the project root with your credentials:

```env
NET_ID=your_netid
PASSWORD=your_password
```

2. Add courses to your cart manually through the UW Madison enrollment website before running the automation.

## Usage

### Basic Usage

```python
from enroll import Enrollment

# Default usage (Fall 2025)
enrollment = Enrollment()
enrollment.run()
```

### Custom Semester

```python
from enroll import Enrollment

# Specify a different semester
enrollment = Enrollment(semester="Spring 2025")
enrollment.run()
```

### Command Line Usage

```bash
uv run enroll.py
```

## How It Works

1. **Browser Setup**: Launches a persistent Chrome browser instance with a dedicated profile
2. **Navigation**: Goes to the UW Madison enrollment page
3. **Authentication**: Automatically logs in using provided credentials
4. **Semester Selection**: Selects the specified semester from the dropdown
5. **Cart Access**: Navigates to the enrollment cart
6. **Course Selection**: Checks all courses in the cart
7. **Validation**: Revalidates the cart before enrollment
8. **Enrollment**: Attempts to enroll in all selected courses
9. **Retry Logic**: If enrollment fails due to invalid appointment time, it retries continuously
10. **Documentation**: Takes screenshots and logs all activities

## Project Structure

```
automate-enrollment/
├── enroll.py          # Main enrollment automation script
├── utils.py           # Utility functions and configuration
├── pyproject.toml     # Project dependencies and metadata
├── .env              # Environment variables (create this)
├── chrome_profile/   # Persistent Chrome browser profile
├── screenshots/      # Enrollment attempt screenshots
└── enrollment.log    # Detailed log file
```

## Configuration Options

### Environment Variables

- `NET_ID`: Your UW Madison NetID
- `PASSWORD`: Your UW Madison password

### Constants (in utils.py)

- `URL`: Enrollment system URL
- `TIMEOUT_MAX`: Maximum timeout for page operations (3 minutes)
- `SCREENSHOTS_DIR`: Directory for storing screenshots

## Logging

The application provides two types of logging:

1. **Console Output**: Colored log messages displayed in the terminal
2. **File Logging**: Detailed logs saved to `enrollment.log`

## Important Notes

- **Course Cart**: You must manually add courses to your cart before running the automation
- **Enrollment Appointments**: The script will continuously retry if your enrollment appointment time hasn't arrived yet
- **Browser Profile**: A persistent Chrome profile is maintained to avoid repeated logins
- **Network Requirements**: Ensure stable internet connection for reliable automation

## License

This project is for educational and personal use. Please ensure compliance with UW Madison's terms of service and academic policies.

## Disclaimer

This tool is provided as-is for educational purposes. Users are responsible for ensuring their use complies with university policies and regulations. The authors are not responsible for any issues arising from the use of this automation tool.
