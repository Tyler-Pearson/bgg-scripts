import atexit
import bgg_config
import signal
import shelve
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


###
# globals
###

msg_url = 'https://boardgamegeek.com/geekmail'

options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

shelve_file = shelve.open(".bgg_messages")


###
# helper fn's
###

def get_bgg_messages():
    bgg_messages = []

    driver.get(msg_url)
    source = driver.page_source

    # log in
    if ("sign in" in source):
        form_usr = driver.find_element(By.ID, "inputUsername")
        form_usr.send_keys(bgg_config.user['username'])
        form_pwd = driver.find_element(By.ID, "inputPassword")
        form_pwd.send_keys(bgg_config.user['password'])
        driver.find_element("xpath", '//button[normalize-space()="Sign In"]').click()
        time.sleep(1)
        source = driver.page_source
    
    # get messages
    soup = BeautifulSoup(source)
    for tag in soup.find_all("table", {"class": "gm_messages"}):
        a = tag.find_all("a")
        bgg_messages.append([a[1].get("name"), a[0].text, a[2].text])

    time.sleep(3)
    return bgg_messages

def get_bgg_shelve():
    try:
        return shelve_file['messages']
    except:
        return []


###
# sys fn's
###

def handle_exit():
    driver.quit()
    shelve_file.close()
    print("bye!")


# core execution loop
def execute():
    print("executing...")
    new_messages = get_bgg_messages()
    # for message in new_messages:
        # print(f'Message: {message[0]}, Sender: {message[1]}, Subject: {message[2]}')

    old_messages = get_bgg_shelve()

    differences = [message for message in new_messages if (message not in old_messages)]
    for message in differences:
        print(f'New message found! Id: {message[0]}, Sender: {message[1]}, Subject: {message[2]}')
    if differences:
        # TODO: Trigger a text message pls
        shelve_file["messages"] = new_messages
        shelve_file.sync() 
    else:
        print("No new messages thx!")
    # next:
        # if any mgs's are new, tell me about it
        # move to github, make config file temporarily empty, add to github, un-empty and add configs to .gitignore
        # transfer this file to ec2 and run as daemon


def main():
    execute()

atexit.register(handle_exit)
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

if __name__=='__main__':
    main()