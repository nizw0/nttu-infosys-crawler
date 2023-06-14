import json
import time
import warnings

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, logging


def fetch_scores():
    # load config
    config = json.load(open('config.json', 'r'))
    if not config:
        raise FileNotFoundError

    # user configuration
    username = config['username']
    password = config['password']
    if not username or not password:
        raise EOFError

    # define path and url
    driver_path = 'C:\\Users\\nizw0\\bin\\geckodriver.exe'
    firefox_path = 'C:\\Program Files\\Firefox Developer Edition\\firefox.exe'
    infosys_url = 'https://infosys.nttu.edu.tw/webClientMain.aspx'

    # init
    options = Options()
    options.binary_location = firefox_path
    options.add_argument('--headless')
    service = Service(driver_path)
    browser = webdriver.Firefox(service=service, options=options)

    warnings.filterwarnings('ignore')
    logging.set_verbosity_error()

    # define processor and model
    processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
    model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')

    # load page
    browser.get(infosys_url)

    for i in range(1, 100):
        # type login data
        browser.find_element(By.ID, 'txtUserName').clear()
        browser.find_element(By.ID, 'txtUserName').send_keys(username)
        browser.find_element(By.ID, 'txtPassword').send_keys(password)
        with open('captcha.png', 'wb') as file:
            img = browser.find_element(By.ID, 'Image1')
            file.write(img.screenshot_as_png)

        # load captcha image
        image = Image.open('captcha.png').convert('L').convert('RGB')
        image.save('captcha-x.png')
        pixel_values = processor(images=image, return_tensors='pt').pixel_values

        # predict
        generated_ids = model.generate(pixel_values)
        captcha_code = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        captcha_code = ''.join([c for c in captcha_code if c.isdigit()])
        if len(captcha_code) != 4 or not captcha_code.isdigit():
            browser.get(browser.current_url)
            continue

        # type captcha
        browser.find_element(By.ID, 'tbCheckCode').clear()
        browser.find_element(By.ID, 'tbCheckCode').send_keys(captcha_code)
        browser.find_element(By.ID, 'OKButton').click()
        if browser.current_url == infosys_url:
            break
        try:
            failure = browser.find_element(By.ID, 'FailureText')
            if failure.text.find(username) != -1:
                browser.find_element(By.ID, 'ReLoginButton').click()
                raise EOFError
            time.sleep(3)
        except Exception:
            break

    time.sleep(3)
    # fetch data
    data = []
    for i in range(1, 5):
        try:
            data_url = 'https://infosys.nttu.edu.tw/n_LearningEffect/Stu_StudyEf_Dashboard.aspx/GetJson'
            headers = {'Content-Type': 'application/json'}
            response = requests.post(data_url, headers=headers)
            if response.status_code != 200:
                response.raise_for_status()
            data = json.loads(response.text)
            data = json.loads(data['d'])
            data.reverse()
            break
        except Exception:
            time.sleep(3)
            continue
    if not data:
        raise requests.RequestException

    # close browser
    browser.close()

    return data
