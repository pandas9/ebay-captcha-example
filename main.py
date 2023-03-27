from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service

import time

import os
import sys

import requests

from random import uniform

import json

from datetime import datetime, timedelta

from anticaptchaofficial.hcaptchaproxyless import *

from urllib.parse import unquote, quote, quote_plus, urlsplit

class Bot:
    captcha_solved_during_session = False
    anticaptcha_key = '*******************'

    def check_solve_captcha(driver, data):
        if Bot.captcha_solved_during_session:
            return 'success'

        try:
            try:
                WebDriverWait(driver, 7.5).until(EC.presence_of_element_located((By.ID, 'captchaFrame')))
                iframe = driver.find_element(By.ID, "captchaFrame")
                driver.switch_to.frame(iframe)
            except:
                pass

            WebDriverWait(driver, 7.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'target-icaptcha-slot')))
            captcha_iframe = driver.find_element(By.CLASS_NAME, 'target-icaptcha-slot').find_elements(By.TAG_NAME, 'iframe')[0]
            captcha_salt = captcha_iframe.get_attribute('data-hcaptcha-widget-id')
            captcha_src = captcha_iframe.get_attribute('src')

            captcha_data = None
            for inpt in driver.find_element(By.ID, 'CentralArea').find_elements(By.TAG_NAME, 'input'):
                if 'captcha-data' in inpt.get_attribute('id'):
                    captcha_data = inpt.get_attribute('value')
                    break
            captcha_data = json.loads(captcha_data)
            captcha_data['pvt'] = 1672415153990
            captcha_data['cvt'] = 1672415154397
            captcha_data['crt'] = 1672415221788

            f_date = datetime.now() + timedelta(seconds=120)

            while True:
                if datetime.now() > f_date:
                    return 'error timeout'

                solver = hCaptchaProxyless()
                solver.set_verbose(1)
                solver.set_key(Bot.anticaptcha_key)
                solver.set_website_url(driver.current_url)
                solver.set_website_key(captcha_src.split('&sitekey=')[-1].split('&')[0])

                g_response = solver.solve_and_return_solution()
                if g_response != 0:
                    captcha_data['token'] = g_response
                    captcha_data_quoted = quote(json.dumps(captcha_data))

                    driver.execute_script(f"""
                    document.getElementsByName("g-recaptcha-response")[0].innerHTML = "{g_response}";
                    document.getElementsByName("h-captcha-response")[0].innerHTML = "{g_response}";
                    document.getElementById("h-captcha-response-{captcha_salt}").innerHTML = "{g_response}";

                    let scr = document.createElement('input');
                    scr.name = 'captchaTokenInput';
                    scr.type = 'hidden';
                    scr.value = "{captcha_data_quoted}";
                    document.getElementById('captcha_form').appendChild(scr);

                    let iframes = document.getElementsByTagName("iframe");
                    iframes[1].setAttribute("data-hcaptcha-response", "{g_response}");

                    captchaCallback(true);
                    """)
                    # document.getElementById('captcha_form').submit();

                    Bot.captcha_solved_during_session = True

                    return 'success'
                else:
                    return f'error {solver.error_code}'
        except:
            return 'not found'

    def login(driver, data):
        try:
            driver.get('https://signin.ebay.com/ws/eBayISAPI.dll?SignIn')
            #time.sleep(999)

            solve_captcha = Bot.check_solve_captcha(driver, data)
            if 'error' in solve_captcha:
                return
            driver.switch_to.default_content()

            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'signin-continue-btn')))
            driver.find_element(By.ID, 'userid').send_keys(data['email'])
            driver.find_element(By.ID, 'signin-continue-btn').click()
            time.sleep(uniform(4.5, 6))

            solve_captcha = Bot.check_solve_captcha(driver, data)
            if 'error' in solve_captcha:
                return
            driver.switch_to.default_content()
            if solve_captcha == 'success':
                time.sleep(uniform(3, 4.5))

            driver.find_element(By.ID, 'pass').send_keys(data['password'])
            driver.find_element(By.ID, 'sgnBt').click()

            time.sleep(uniform(3, 4.5))

            return 'success'
        except:
            return 'error'

if __name__ == '__main__':
    # Initiate a driver and pass it to login
    # Pass data such as email password etc
    driver = None
    data = { }
    Bot.login(driver, data)
