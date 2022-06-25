import pika, sys, os
import os
import time
import json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

chrome_options = webdriver.ChromeOptions()  
chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")
chrome_options.add_argument("window-size=800,600")
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-browser-side-navigation')
chrome_options.add_argument('--disable-features=VizDisplayCompositor')

driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"), options=chrome_options)
driver.maximize_window()

connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ.get("RABBITMQ_HOST")))
channel = connection.channel()

channel.queue_declare(queue='coordinate')

def callback(ch, method, properties, body):
    print("[x] Received {}".format(body.decode()))

    try:
        process(body.decode())
    except TimeoutException as e:
        print("RETRYING... ", body.decode())
        process(body.decode())

def process(data):
    coordinate = data.split(",")
    url = "https://www.google.com/maps/@{},{},371m/data=!3m1!1e3".format(coordinate[0], coordinate[1])
    
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="omnibox-singlebox"]/div[1]/div[1]/button')))
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="omnibox-singlebox"]/div[1]/div[1]/button').click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="settings"]/div/div[1]')))
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//*[@id="settings"]/div/div[1]').click()
    time.sleep(0.3)
    driver.save_screenshot("photos/{} - {}.png".format(coordinate[0], coordinate[1]))

try:
    channel.basic_consume(queue='coordinate', on_message_callback=callback, auto_ack=True)

    print('[*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
except KeyboardInterrupt:
    print('Interrupted')
    try:
        sys.exit(0)
        driver.close()
    except SystemExit:
        os._exit(0)
        driver.close()

