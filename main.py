from decouple import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import datetime
import argparse
import sys

import time as Timer
GROUP_NAME = "BB"
HEADLESS = False 
DRIVER_PATH = config("DRIVER_PATH")
LIBRARY_ROOM_RESERVE_URL = 'https://nyu.libcal.com/reserve/dibner-large-group-study'
#LIBRARY_ROOM_RESERVE_URL = 'https://nyu.libcal.com/reserve/dibner-large-group-study'
TIME_SLOT_CLASS_XPATH = "//*[@class='fc-timeline-event-harness']"
WAIT_DELAY = 3
TIME_SLOT_ARIA_LABEL_XPATH = "//*[contains(@aria-label,'{time}')]"
CHANGE_DATE_DAY_XPATH = "//td[@class='day' and contains(text(),'{day}')]"
SUBMIT_BUTTON_XPATH = "//button[@id='submit_times']"
LIBRARY_LOGIN_URL = "https://login.library.nyu.edu/"
NYU_LOGIN_URL = "https://login.library.nyu.edu/users/auth/nyu_shibboleth?auth_type=nyu&institution=NYU"
NYU_LOGIN_USERNAME = config('NYU_USERNAME')
NYU_LOGIN_PASSWORD = config('NYU_PASSWORD')
TIME_FORMAT = "{hour}:{min}{meridian}"

room_prio = [""]

def login_to_NYU(driver: webdriver):
    wait_driver = WebDriverWait(driver, 60)
    try: 
        username = wait_driver.until(EC.presence_of_element_located((By.XPATH, "//input[@id='username']" )))
        password = wait_driver.until(EC.presence_of_element_located((By.XPATH, "//input[@id='password']" )))
        login = wait_driver.until(EC.presence_of_element_located((By.XPATH, "//button[@name='_eventId_proceed']" )))
    except TimeoutException:
        print("ERROR COULD NOT FIND USERNAME/PASSWORD INPUTS: probably did not load in") 
        return 
    username.send_keys(NYU_LOGIN_USERNAME)
    password.send_keys(NYU_LOGIN_PASSWORD)
    login.click()
    try: 
        trust_browser_btn = wait_driver.until(EC.element_to_be_clickable((By.XPATH, "//button[@id='trust-browser-button']" )))
        trust_browser_btn.click()
    except: 
        print("Trust Broswer Btn did not appear")   
    try:
        wait_driver.until(lambda driver: "duosecurity" not in driver.current_url)
    except TimeoutException: 
        sys.exit("ERROR FAILED TO LOGIN: probably forgot to accept duo security")

def selectRoom(driver: webdriver,wait_driver:WebDriverWait, time:str, day: str, room = None): 
    driver.get(LIBRARY_ROOM_RESERVE_URL)
    #selecting time slot based on time

    #check if day is today 
    today_day = None 
    
    Go_To_Date_Btn = wait_driver.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Go To Date']")))
    Go_To_Date_Btn.click()
    today_dt = datetime.datetime.combine(datetime.date.today(), datetime.time(second=0, hour = 0, minute=0))
    # today_unix = str(int(today_dt.timestamp() * 1000))
    today_day = today_dt.day
    print("today: ", today_day)
    try:
        if(day != today_day):
            random_object =  wait_driver.until(EC.element_to_be_clickable((By.XPATH, "//th[@class='dow']")))
            random_object.click() #there is a problem when the go to date btn is selected it a pop up appears where it blocks some of the days this is to deselect the btn so the pop up disappears
            change_date_day_btn = wait_driver.until(EC.element_to_be_clickable((By.XPATH, CHANGE_DATE_DAY_XPATH.format(day = day))))
            change_date_day_btn.click()
    except TimeoutException:        
        print("DATE NOT FOUND:", day)
        return
    try:
        wait_driver.until(EC.presence_of_element_located((By.XPATH, TIME_SLOT_CLASS_XPATH)))
    except TimeoutException:
        sys.exit("ERROR COULD NOT FIND TIME_SLOT_CLASS_XPATH: MOST LIKELY THE PAGE DID NOT LOAD IN OR THE XPATH WAS CHANGED")
    slots = driver.find_elements(By.XPATH, TIME_SLOT_ARIA_LABEL_XPATH.format(time = time))
    if(room):
        room_slot = None
        for slot in slots: 
            label = str(slot.get_attribute("aria-label"))
            if("Available" in label and room in label): 
                room_slot = slot
        if(room_slot): 
            room_slot.click()
        else: 
            print("TIME SLOT NOT FOUND FOR ROOM:", room, " ON TIME:", time, "FOR DAY:", day)
    else: 
        available_slots = []
        for slot in slots: 
            label = str(slot.get_attribute("aria-label"))
            if("Available" in label): 
                available_slots.append(slot)
        if(len(available_slots) != 0): 
            available_slots[0].click()
        else: 
            print("TIME SLOT NOT FOUND:", time, "FOR DAY:", day)
            return
    return True 
def reserveRoom(driver: webdriver, wait_driver:WebDriverWait, day = None, time = None  ):
    submit_button = None; 
    try:
        wait_driver.until(EC.presence_of_element_located((By.XPATH, SUBMIT_BUTTON_XPATH)))
    except TimeoutException:
        print("ERROR COULD NOT FIND SUBMIT BUTTON: most likely button XPATH changed")
        return False 
    print("Submit Button Found")
    try:
        submit_button = wait_driver.until(EC.element_to_be_clickable((By.XPATH, SUBMIT_BUTTON_XPATH)))
        submit_button.click()
    except TimeoutException: 
        print("ERROR COULD NOT SELECT SUBMIT BUTTON: it probably did not load in properly")
        return False 

    try: 
        wait_driver.until(lambda driver: driver.current_url != LIBRARY_ROOM_RESERVE_URL)
        print("URL HAS CHANGED")
    except TimeoutException:
        print("ERROR URL DID NOT CHANGE AFTER CLICKING SUBMIT BUTTON")
        return False 
        
    
    if(driver.current_url == LIBRARY_LOGIN_URL): 
        try:
            nyu_login_ref = wait_driver.until(EC.element_to_be_clickable((By.XPATH,'//*[@href="/users/auth/nyu_shibboleth?auth_type=nyu&institution=NYU"]')))
            nyu_login_ref.click()
        except TimeoutException: 
            return False 
        login_to_NYU(driver)
    
    try:
        continue_btn = wait_driver.until( EC.element_to_be_clickable((By.XPATH,'//button[@name="continue"]') ))
        continue_btn.click()
    except TimeoutException:
        return False 
        
    try: 
        submit_booking_btn = wait_driver.until( EC.element_to_be_clickable((By.XPATH, '//button[@id="s-lc-eq-bform-submit"]')) )
        group_name = wait_driver.until( EC.presence_of_element_located((By.XPATH, "//input[@name='nick']")) )
        group_name.send_keys(GROUP_NAME)
        submit_booking_btn.click()
    except:
        return False 

    try: 
        wait_driver.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Thank you!')]")))
        print("Reserved room at day:", day, "time:",time)
    except TimeoutException: 
        print("FAILED TO RESERVER ROOM AT DAY:", day, "TIME:",time)
        return False 
    return True

def reserve_time_range_for_large_rooms(driver: webdriver,wait_driver:WebDriverWait, start: int, end: int, day: str, interval: int, room = None): 
    if(start >= end):
        print("Error: Start >= End") 
        return False
    if(end > 24 and start < 1): 
        print("Error: Invalid time range")
        return False
    for hour in range(start,end,interval):
        meridian = "am" if hour//12 == 0 else "pm" 
        hour = ((hour-1)%12)+1
        time = TIME_FORMAT.format(hour=str(hour), min ="00", meridian=meridian)
        print(time)
        res = selectRoom(driver, wait_driver, time , day, room)
        if(res):
            reserveRoom(driver, wait_driver, day, time)
    return True 


def reserve_day_range_and_time_range_for_large_rooms(driver: webdriver, wait_driver, start_day:int , end_day:int , start_time:int, end_time:int, interval: int, room = None):
    if(start_day > end_day):
        print("ERROR: start_day > end_day")
        return False 
    if(start_day < 1 and end_day > 31): 
        print("ERROR: Invalid day range")
        return False 
    if(start_time >= end_time):
        print("Error: Start_time >= End_time") 
        return False
    if(end_time > 24 and start_time < 1): 
        print("Error: Invalid time range")
        return False
    for day in range(start_day, end_day+1): 
        reserve_time_range_for_large_rooms(driver, wait_driver, start_time,end_time, str(day), interval, room)
if __name__ == "__main__":
    day_start, day_end, time_start, time_end, interval, room = None, None, None, None, None, None 
    parser = argparse.ArgumentParser(description='NYU Libcal Library Room Reserver')
    parser.add_argument('--DTRange', help=
        'The date and time range for reservation day-start,day-end,time-start,time-end,room (int,int,int,int, int, str(optional) ), time is in military time. Time interval is the interval in hours that libcal allows you to reserve (this is different dependent on types of room) ')
    parser.add_argument('--URL', help=
        'The URL of an NYU Libcal room reservation page, defaulted as Dibner Large Library rooms')
    cmdline = parser.parse_args()
    if cmdline.DTRange is not None: 
        parts = cmdline.DTRange.split(",")
        if(len(parts) == 5):
            [day_start, day_end, time_start, time_end, interval] = [int(x) for x in parts]
        elif(len(parts) == 6): 
            [day_start, day_end, time_start, time_end, interval] = [int(x) for x in parts[0:5]]
            room = parts[5]
            
        else: 
            sys.exit("Invalid Amount of Date and Time Range arguments --help")
    else: 
        sys.exit("Did not set Date and Time Range argument --help")
    if cmdline.URL is not None: 
        print(cmdline.URL)
        LIBRARY_ROOM_RESERVE_URL = cmdline.URL
    driver = None
    if(HEADLESS): 
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    else:
        driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    wait_driver = WebDriverWait(driver, WAIT_DELAY) 
    reserve_day_range_and_time_range_for_large_rooms(driver,wait_driver,day_start,day_end, time_start,time_end, interval, room)
    driver.quit()

    