# README

## Overview

This Python script automates the process of logging into the Infosys NTTU website, handling CAPTCHA recognition using the TrOCR model, and fetching data related to student study effectiveness. It uses Selenium to interact with the web page, TrOCR for CAPTCHA decoding, and requests for data fetching.

## Requirements

Before running the script, ensure you have the following dependencies installed:

- Python 3.x
- `requests`
- `alive-progress`
- `Pillow` (PIL)
- `selenium`
- `transformers`

You can install the required Python packages using pip:

```bash
pip install requests alive-progress Pillow selenium transformers
```

Additionally, you'll need:

- [GeckoDriver](https://github.com/mozilla/geckodriver/releases) for Firefox
- [Firefox Developer Edition](https://www.mozilla.org/en-US/firefox/developer/) installed on your system

## Configuration

1. **Config File**

   Create a `config.json` file in the same directory as your script with the following format:

   ```json
   {
       "username": "your_username",
       "password": "your_password"
   }
   ```

   Replace `"your_username"` and `"your_password"` with your actual Infosys credentials.

2. **Driver Path**

   Update the `driver_path` and `firefox_path` variables in the script with the paths to your GeckoDriver executable and Firefox Developer Edition installation.

## Running the Script

1. Ensure the `config.json` file is correctly set up and paths are correctly configured in the script.

2. Execute the script:

   ```bash
   python script_name.py
   ```

   Replace `script_name.py` with the name of your Python script file.

## Script Workflow

1. **Page Loading**

   The script starts by loading the Infosys login page.

2. **Login Process**

   - Logs in using the provided username and password.
   - Captures and processes the CAPTCHA image using TrOCR to decode it.
   - Attempts to log in with the decoded CAPTCHA.

3. **Data Fetching**

   - After a successful login, navigates to the student study effectiveness dashboard.
   - Fetches and processes the JSON data related to study effectiveness.
   - Calculates and prints the average score and total credits.

4. **Cleanup**

   - Closes the browser after processing.

## Error Handling

- The script will retry CAPTCHA recognition up to 100 times before giving up.
- If data fetching fails, it will attempt multiple times before raising an exception.

## Notes

- Ensure that your Firefox Developer Edition and GeckoDriver versions are compatible.
- This script operates in headless mode. You can remove the `--headless` argument if you want to see the browser in action.

## License

This script is for educational and personal use. Modify and use it at your own risk.
