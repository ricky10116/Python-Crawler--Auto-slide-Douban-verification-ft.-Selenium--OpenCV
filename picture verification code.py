from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time, re
from lxml import etree
from urllib import request
from PIL import Image
import cv2

from matplotlib import pyplot as plt
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# OpenCV reference : https://zwindr.blogspot.com/2017/02/python-opencv-matchtemplate.html
def opencv():
    img = cv2.imread('captcha.png')
    img2 = img.copy()
    template = cv2.imread('pattern.png')
    w = template.shape[1]
    h = template.shape[0]

    # All the 6 methods for comparison in a list
    methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
               'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
    methods = ['cv2.TM_CCOEFF']
    for meth in methods:
        img = img2.copy()
        method = eval(meth)

        # Apply template Matching
        res = cv2.matchTemplate(img, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        cv2.rectangle(img, top_left, bottom_right, 255, 2)
        print("top_left=",top_left)
        plt.subplot(121), plt.imshow(res, cmap='gray')
        plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        plt.subplot(122), plt.imshow(img)
        plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        plt.suptitle(meth)

        plt.show()
        break

    return top_left


# https://chromedriver.chromium.org/downloads
driver_path = r"D:\ProgramApp\chromedriver\chromedriver.exe"
driver = webdriver.Chrome(executable_path=driver_path)
actions = ActionChains(driver)
driver.get('https://accounts.douban.com/passport/login_popup?login_source=anony') #
time.sleep(2)

#### method 1 ####
# driver.find_element_by_xpath("//div[@class='account-body-tabs']//li[@class='account-tab-account']").click()  # to password login
# driver.find_element_by_id("username").click()
# driver.find_element_by_id("username").send_keys("python")

#### method 2 ####
login = driver.find_element_by_xpath("//div[@class='account-body-tabs']//li[@class='account-tab-account']")  # to password login

actions = ActionChains(driver)
actions.move_to_element(login)
actions.click(login)
actions.perform()

account = driver.find_element_by_id("username")
actions.move_to_element(account)
actions.send_keys_to_element(account,'python')
actions.perform()

actions = ActionChains(driver)
password = driver.find_element_by_id("password")
actions.move_to_element(password)
actions.send_keys_to_element(password,'python')
actions.perform()
# //div[@class='account-form-field-submit']/a

while True :
    driver.find_element_by_xpath("//div[@class='account-form-field-submit ']/a").click()
    time.sleep(2)
    html1 = etree.HTML(driver.page_source)
    short = html1.xpath("//iframe[@id='tcaptcha_iframe']/@src")
    print(short) # []
    if (short ) :
        print("break")
        break
URL = html1.xpath("//iframe[@id='tcaptcha_iframe']/@src")
print("URL=",URL)
time.sleep(1)

WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@id='tcaptcha_iframe']")))
time.sleep(5)
inputTag = driver.find_element_by_xpath('//div[@id="tcaptcha_drag_thumb"]')
imgurTag = driver.find_element_by_xpath('//div[@class="tc-bg"]/img').get_attribute('src')  # mind

# https://stackoverflow.com/questions/28078812/get-iframe-src-via-xpath

print("imgurTag=",imgurTag )

#### need to remove "*"
imgurl2 = re.sub(r'\*','',imgurTag)
print("imgurl2=",imgurl2 )

request.urlretrieve(imgurl2, 'captcha.png')  # save image

position = opencv()
print(position)
newpos= ( position[0]- 76 ) * 0.4176  # the length iframe is 284 and the length opencv picture is  680   284/680  get convert ratio
print("newpos=",newpos)
inputTag = driver.find_element_by_xpath('//div[@id="tcaptcha_drag_thumb"]')

# #
action = ActionChains(driver)
webdriver.ActionChains(driver).drag_and_drop_by_offset(inputTag, newpos-1, 0).perform()
time.sleep(1)
webdriver.ActionChains(driver).drag_and_drop_by_offset(inputTag, 1, 0).perform()

time.sleep(2)
# #

print("END")



