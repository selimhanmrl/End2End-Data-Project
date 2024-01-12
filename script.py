import time
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import pandas as pd
import boto
import boto.s3
import sys
from boto.s3.key import Key
import logging
import os


file_path = os.path.join( time.strftime("%d_%m_%Y")+".log")
tracer = logging.getLogger('Logger')
tracer.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.INFO, format="%(name)s %(asctime)s: %(levelname)s: %(message)s", handlers=[logging.FileHandler(file_path), logging.StreamHandler()])

firefox_options = Options()
firefox_options.add_argument('-private')
firefox_options.add_argument('--headless')

driver = webdriver.Firefox(options=firefox_options)

tracer.info("Script started")
from time import sleep


df = pd.read_csv('hrefs.csv')
cargo = []
link = []
cargo = []
price = []
fraction = []
stock = []
name = []
model = []
lastPriceUpdates = []
store = []
brand = []

last = pd.DataFrame({'name':name, 'model': model,  'price': price,  'cargo': cargo,'stock': stock,'lastPriceUpdates': lastPriceUpdates, 'store': store})

for ref in range(len(df)):
    try:
        driver.get(df.iloc[ref]['href'])
    except:
         print(df.iloc[ref]['href'] + " 404 not found")
    try:
        l = driver.find_element(by=By.ID, value="SAP")
        driver.execute_script("arguments[0].click();",l)
        time.sleep(1)
    except:
        pass
    cargo = []
    link = []
    cargo = []
    price = []
    fraction = []
    stock = []
    name = []
    model = []
    lastPriceUpdates = []
    store = []
    brand = []
    cargo_ = driver.find_elements(by=By.XPATH, value='//*[@class="pb_v8"]//em')
    cargo_ = cargo_[1:]
    price_ = driver.find_elements(by=By.XPATH, value='//*[@class="pb_v8"]//span[@class="pt_v8"]')
    price_ = price_[1:]
    stock_ = driver.find_elements(by=By.XPATH, value='//*[@class="w_v8"]//*[@class="stock_v8"] | //*[@class="w_v8"]//*[@class="stock_v8 no-stock"]')
    stock_ = stock_[1:]
    lastPriceUpdates_ = driver.find_elements(by=By.XPATH, value='//*[@class="w_v8"]//*[@class="bd_v8"]//i')
    store_ = driver.find_elements(by=By.XPATH, value='//*[@class="w_v8"]//*[@class="v_v8"]//img | //*[@class="w_v8"]//*[@class="v_v8"]//b | //*[@class="w_v8"]//b[@class="n_url"]')
    name_ = driver.find_elements(by=By.XPATH, value='//*[@class="w_v8"]//*[@class="pn_v8"]')
    store_ = driver.find_elements(by=By.XPATH, value='//*[@class="w_v8"]//*[@class="v_v8"]//img | //*[@class="w_v8"]//*[@class="v_v8"]//b | //*[@class="w_v8"]//b[@class="n_url"]')
    try:
        brand_ = driver.find_element(by=By.XPATH, value='/html/body/main/div[1]/div[1]/div[1]/a[1]')
    except:
        brand_ = None
    productDOM = driver.find_elements(by=By.XPATH, value='//*[@class="pl_v8 pr_v8"]//li')
    button  = driver.find_elements(by=By.XPATH, value='//*[@class="pl_v8 pr_v8"]//li//a')

    for i in range(len(productDOM)):
        try:
            cargo.append(cargo_[i].text)
            price.append(price_[i].text)
            stock.append(stock_[i].text)
            model.append(df["model"][ref])
            name.append(name_[i].text)
            if brand_ != None:
                brand.append(brand_.text)
            else:
                brand.append("N/A")
            lastPriceUpdates.append(lastPriceUpdates_[i].text)
            if store_[i].get_attribute("tagName") == "IMG":
                    if store_[i].find_elements(By.XPATH,(".."))[0].text != "" and "Yorum" not in store_[i].find_elements(By.XPATH,(".."))[0].text:
                        store.append(store_[i].get_attribute("alt") + store_[i].find_elements(By.XPATH,(".."))[0].text)
                    else:
                        store.append(store_[i].get_attribute("alt"))
            elif store_[i].get_attribute("tagName") == 'B':
                    store.append(store_[i].text)
            else:
                    store.append(store_[i].text)
        except:
            tracer.warning("Array Eksik Model: " + df["model"][ref])

    flag = 1
    for i in range(len(lastPriceUpdates)):
        if "dün" in lastPriceUpdates[i].lower():
            lastPriceUpdates[i] =  time.strftime("%d/%m/%Y", time.localtime(time.time() - 86400))
        else:
            lastPriceUpdates[i] = time.strftime("%d/%m/%Y")
    try:
        last = pd.concat([last, pd.DataFrame({'name':name, 'brand':brand, 'model': model,  'price': price,  'cargo': cargo,'stock': stock,'lastPriceUpdates': lastPriceUpdates, 'store': store})],ignore_index=True)
    except:
        tracer.warning("CSV Eksik Model: " + df["model"][ref])


    time.sleep(5)

driver.close()

last.to_parquet("FiyatListesi_"+time.strftime("%d_%m_%Y")+'.parquet')

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

bucket_name = ''
conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY)


bucket = conn.create_bucket(bucket_name,
    location=boto.s3.connection.Location.DEFAULT)

testfile = "FiyatListesi_"+time.strftime("%d_%m_%Y")+'.parquet'
tracer.info('Uploading %s to Amazon S3 bucket %s' % \
   (testfile, bucket_name))

def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()


k = Key(bucket)
k.key = testfile
k.set_contents_from_filename(testfile,
    cb=percent_cb, num_cb=10)
tracer.info("File uploaded to S3")
tracer.info("Script finished" + time.strftime("%d/%m/%Y %H:%M:%S"))