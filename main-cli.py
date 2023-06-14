import json
import os
import time
import warnings
from pprint import pprint

import requests
from alive_progress import alive_bar, config_handler
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, logging

# load config
config = json.load(open('config.json', 'r'))
if not config:
    raise FileNotFoundError

# user configuration
username = config['username']
password = config['password']

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

config_handler.set_global(theme='classic', title_length=15, length=25, elapsed=False, stats=False, dual_line=True)

warnings.filterwarnings('ignore')
logging.set_verbosity_error()

# define processor and model
processor = TrOCRProcessor
model = VisionEncoderDecoderModel

# clear log
os.system('clear')


def main():
    print('program started')

    # load page
    with alive_bar(1, title='loading page') as bar:
        browser.get(infosys_url)
        bar(1.)

    with alive_bar(100, title='logging in') as bar:
        # load processor and model
        bar.text('loading processor and model')
        global processor, model
        processor = processor.from_pretrained('microsoft/trocr-base-printed')
        model = model.from_pretrained('microsoft/trocr-base-printed')

        for i in range(1, 100):
            bar()

            # type login data
            bar.text('typing user credentials')
            browser.find_element(By.ID, 'txtUserName').clear()
            browser.find_element(By.ID, 'txtUserName').send_keys(username)
            browser.find_element(By.ID, 'txtPassword').send_keys(password)
            with open('captcha.png', 'wb') as file:
                img = browser.find_element(By.ID, 'Image1')
                file.write(img.screenshot_as_png)

            # load captcha image
            bar.text('fetching captcha')
            image = Image.open('captcha.png').convert('L').convert('RGB')
            image.save('captcha-x.png')
            pixel_values = processor(images=image, return_tensors='pt').pixel_values

            # predict
            bar.text('computing captcha')
            generated_ids = model.generate(pixel_values)
            captcha_code = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            captcha_code = captcha_code.replace(' ', '')
            print(captcha_code)
            if len(captcha_code) != 4 or not captcha_code.isdigit():
                browser.get(browser.current_url)
                bar.text('another round')
                continue

            # type captcha
            bar.text('logging in')
            browser.find_element(By.ID, 'tbCheckCode').clear()
            browser.find_element(By.ID, 'tbCheckCode').send_keys(captcha_code)
            browser.find_element(By.ID, 'OKButton').click()
            try:
                browser.find_element(By.ID, 'FailureText')
                time.sleep(3)
                bar.text('another round')
            except Exception:
                print('login successful')
                bar(100 - i)
                break

    time.sleep(3)
    # fetch data
    data = []
    with alive_bar(5, title='fetching data') as bar:
        for i in range(1, 5):
            bar()
            try:
                data_url = 'https://infosys.nttu.edu.tw/n_LearningEffect/Stu_StudyEf_Dashboard.aspx/GetJson'
                headers = {'Content-Type': 'application/json; charset=utf-8'}
                response = requests.post(data_url, headers=headers)
                if response.status_code != 200:
                    response.raise_for_status()
                data = json.loads(response.text)
                data = json.loads(data['d'])
                data.reverse()
                bar(5 - i)
                break
            except Exception:
                time.sleep(3)
                continue
    if not data:
        raise requests.RequestException

    avg_score = 0
    sum_credit = 0
    for datum in data:
        pprint(datum)
        avg_score += datum['avg_score']
        sum_credit += datum['sum_credit']
    avg_score = avg_score / len(data)
    print(f'average score: {avg_score}, total credit: {int(sum_credit)}')

    # close browser
    browser.close()


if __name__ == '__main__':
    main()
