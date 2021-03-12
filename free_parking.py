import subprocess
import logging
import datetime
import sys
import os
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

LOGGER = logging.getLogger(__name__)

DIR_NAME = os.path.dirname(os.path.realpath(__file__))
F_DRIVER = os.path.join(DIR_NAME, r'Driver\geckodriver.exe')
CACHE = os.path.join(DIR_NAME, r"Phone_Results\cache\records.txt")
PROFILE = os.path.join(DIR_NAME, r'Profile\rust_mozprofileNODzu1')
RESULTS_FOLDER = os.path.join(DIR_NAME, r'Phone_Results\\')
BASE_PAGE = "https://payments.wikimedia.org/index.php/Special:GatewayFormChooser?payment_method=amazon&recurring=" \
            "false&currency_code=USD&country=US&uselang=en&amount=1&utm_medium=wmfSite&utm_campaign=navButton&utm_" \
            "source=113.default~default~default~default~control.amazon&utm_key=vw_430.vh_1248.otherAmt_1.time_10"
DOLLAR_AMOUNT = 1


def reward_response():
    print_results(True)
    LOGGER.info("Success! Found Phone")


def punishment_response():
    print_results(False)
    LOGGER.info("GRRRR punishing")
    if not have_donated_today_already():
        donate_to_wikipedia(actually_do_it=True)
    else:
        LOGGER.info("Stopping process early because I've already donated")


def print_results(success):
    addendum = "--reward" if success else "--punishment"
    file_name = RESULTS_FOLDER + datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S") + addendum + ".txt"

    output_handler = logging.FileHandler(file_name)
    LOGGER.addHandler(output_handler)
    LOGGER.info("Just added handler!!!")


def get_element_by_xpath(web_object, xpath):
    try:
        element = web_object.find_element_by_xpath(xpath)
        return element
    except NoSuchElementException as e:
        LOGGER.critical("couldnt find" + str(e))
        return False


def get_element_by_selector(web_object, selector):
    try:
        element = web_object.find_element_by_css_selector(selector)
        return element
    except NoSuchElementException as e:
        LOGGER.critical("couldnt find" + str(e))
        return False


def donate_to_wikipedia(actually_do_it=False):
    LOGGER.info("Opening base web page.....")

    web_object = create_web_object_with_base_page()
    handle_continue_page(web_object)

    LOGGER.info("Analyzing elements on page.....")
    donate_button = get_element_by_xpath(web_object, '//*[@id="paymentSubmitBtn"]')
    usd_field = get_element_by_xpath(web_object, '//*[@id="selected-amount"]')

    if usd_field and donate_button:
        verify_donation_requirements_and_submit(donate_button, usd_field, actually_do_it=actually_do_it)
    else:
        LOGGER.critical("Something is wrong... didn't find usd_file or donate_button.... not moving forward")

    web_object.close()


def create_web_object_with_base_page():
    options = webdriver.FirefoxOptions()
    options.add_argument("-profile " + PROFILE)
    web_object = webdriver.Firefox(executable_path=F_DRIVER, options=options,
                                   service_args=["--marionette-port", "2828"])
    web_object.get(BASE_PAGE)
    time.sleep(2)
    return web_object


def handle_continue_page(web_object):
    LOGGER.info("Looking for continue page....")
    continue_button = get_element_by_xpath(web_object, '//*[@id="ap-oaconsent-agree-button"]/span/button')
    if continue_button:
        LOGGER.info("Found the continue page.... clicking")
        continue_button.click()
        time.sleep(2)
    else:
        LOGGER.info("Continue page not found.... no big deal.... lets assume donation page is up")


def verify_donation_requirements_and_submit(donate_button, usd_field, actually_do_it=False):
    LOGGER.info("Found the donate page.... verifying and donating if meets requirements")
    usd_amount = usd_field.get_attribute("innerHTML").strip()
    LOGGER.info("Dollar amount found: {}, dollar amount wanted ${}.00".format(usd_amount, DOLLAR_AMOUNT))
    if usd_amount == "$" + str(DOLLAR_AMOUNT) + ".00":
        write_today_to_donation_cache()
        if actually_do_it:
            LOGGER.info("Donating!!!!!")
            donate_button.click()
            time.sleep(2)
        else:
            LOGGER.info("Would've donated if bool told me to!!!")
    else:
        LOGGER.critical("Found both page elements.... but USD amount is wrong.....")


def have_donated_today_already():
    with open(CACHE, 'a+') as f:
        f.seek(0)
        today = datetime.date.today().strftime('%Y-%m-%d')
        for line in f:
            if line.strip() == str(today):
                LOGGER.info("Already donated today!!!")
                return True
        return False


def write_today_to_donation_cache():
    today = datetime.date.today().strftime('%Y-%m-%d')
    with open(CACHE, 'a+') as f:
        LOGGER.info("Writing {} to cache".format(str(today)))
        f.write(str(today) + '\n')


def is_phone_connected():
    windows = 'nt' in os.name

    if not windows:
        cmd = "ioreg -p IOUSB -w0 | sed 's/[^o]*o //; s/@.*$//' | grep -v '^Root.*'"
        ret = subprocess.run(cmd, shell=True, capture_output=True)
        if "iPhone" in str(ret.stdout):
            return True
    else:
        cmd = 'C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe Get-PnpDevice'
        ret = subprocess.run(cmd, capture_output=True)
        for line in ret.stdout.split(b'\n'):
            if b'Apple iPhone' in line and b'OK' in line and b'Unknown' not in line:
                return True
    return False


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    LOGGER.debug("Starting Script at {}".format(datetime.datetime.now()))

    phone_connected = is_phone_connected()
    if phone_connected:
        reward_response()
    else:
        punishment_response()


