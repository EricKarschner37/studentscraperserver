import requests
import cookielib
from bs4 import BeautifulSoup
from collections import Counter

def getDigits(string):
    new = ''
    for i in string:
        if i.isdigit():
            new += i
    return new

header = {'user-agent' : "Mozilla/5.0 (X11; CrOS x86_64 11021.56.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.76 Safari/537.36"}

#Retrieve information from Yabla
def yabla():
	yabla_url = "https://spanish.yabla.com/login.php"
	username = "erickarschner@gmail.com"
	password = "Iwant$20"
	yabla_url += "?username=" + username + "&password=" + password

	r = requests.get(yabla_url, headers=header)
	c = r.content
	yabla_soup = BeautifulSoup(c, 'html.parser')
	all_link = yabla_soup.find('a', class_='all')
	upcoming_link = yabla_soup.find('a', class_='upcoming')
	past_link = yabla_soup.find('a', class_='past_due')
	complete_link = yabla_soup.find('a', class_='complete')

	try:
	    all = all_link.text.strip()
	except:
	    all = "0"
	try:
	    upcoming = upcoming_link.text.strip()
	except:
	    upcoming = "0"
	try:
	    past = past_link.text.strip()
	except:
	    past = "0"
	try:
	    complete = complete_link.text.strip()
	except:
	    complete = "0"

	all = getDigits(all)
	upcoming = getDigits(upcoming)
	past = getDigits(past)
	complete = getDigits(complete)

	yabla_message = "On Yabla, you have " + all + " total assignments. " + upcoming + " upcoming, " + past + " past due, and " + complete + " complete."

	if upcoming != "0":
	    upcoming = yabla_soup.select('div.sas_upcoming div.inside_col')
	    count = Counter([list(assignment.children)[2].strip() for assignment in upcoming[2::5]])
	    print count
	    yabla_message += " Of your upcoming assignments, you have: "
	    last_day = ""
	    for i in count:
		yabla_message += "" + str(count[i]) + " due on " + i + ","
		last_day = i
	    yabla_message = yabla_message[:-1] + "."
	return yabla_message

#Retrieve information from Cengage
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import time

def cengage():
	options = Options();
	options.add_argument("--headless");

	driver = webdriver.Firefox(firefox_options=options)

	cengage_url = "https://nglsync.cengage.com/portal/Account/LogOn"
	cengage_message = "On Cengage, you have "


	driver.get(cengage_url)

	driver.find_element_by_id("schoolSearchText").send_keys("Hughesville")
	first_window = driver.current_window_handle

	try:
	    element = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.CLASS_NAME, "auto-complete-selection-item"))
	    )
	finally: element.click()

	driver.find_element_by_name("UserName").send_keys("ekarschner")
	driver.find_element_by_name("Password").send_keys("Hanukah7")
	driver.find_element_by_id("login_message-bttn").click()
	print driver.current_window_handle
	driver.save_screenshot('/tmp/test0.png')
	try:
	    element = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.LINK_TEXT, "Launch Course"))
	    )
	finally: element.click()
	time.sleep(20)
	driver.save_screenshot('/tmp/test.png')
	print driver.window_handles
	window_handles = driver.window_handles
	for window in window_handles:
		driver.switch_to.window(window)
		print driver.title
	new_window = window_handles[1]
#	new_window = [window for window in driver.window_handles if window != first_window][0]
	driver.save_screenshot('/tmp/test1.png')
	time.sleep(5)
#	driver.switch_to.window(first_window)
	driver.switch_to.window(new_window)
	driver.save_screenshot('/tmp/test2.png')
#	driver.close()
#	driver.switch_to.window(new_window)
	try:
	    element = WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.CLASS_NAME, "icon-calendar"))
	)
	finally: element.click()

	time.sleep(3) 
	current_week = driver.find_element_by_xpath("//div[div/@aria-expanded='true']")

	day_divs = current_week.find_elements_by_xpath("//div[div/@class='day-bar']")
	no_assignments = True
	for day in day_divs:
	    div = day.find_element_by_tag_name("div")
	    divs = div.find_elements_by_tag_name("div")
	    month = divs[0].text.strip()
	    day = divs[1].text.strip()
	    
	    activities = div.find_elements_by_class_name("activities-wrapper")
	    cengage_message += str(len(activities)) + " assignment(s) due on " + month + getDigits(day) + ", "
	    no_assignments = False\

	if no_assignments:
	    cengage_message += "no assignments due this week!"
	else:
	    cengage_message = cengage_message[:-2] + "."
	driver.close()
	return cengage_message



#Retrieve data from VHLCentral
def vhlcentral():
	vhl_url = "https://www.vhlcentral.com/"
	username = "erickarschner@gmail.com"
	password = "Iwant$20"

	driver.get(vhl_url)
	driver.find_element_by_id("user_session_username").send_keys(username)
	driver.find_element_by_id("user_session_password").send_keys(password)
	driver.find_element_by_name("commit").click()
	driver.find_element_by_link_text("Temas").click()

#Combine the messages from each service
yabla_message = yabla()
cengage_message = cengage()
message = yabla_message + "\n\n" + cengage_message

#Send the message to the user's email address

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

msg = MIMEMultipart()
msg['From'] = "studentscraper@gmail.com"
msg['To'] = "erickarschner@gmail.com"
msg['Subject'] = "Your Homework Assignments"
msg.attach(MIMEText(message, 'plain'))

import smtplib

s = smtplib.SMTP('smtp.gmail.com',587)
s.ehlo()
s.starttls()
s.login('studentscraper@gmail.com','f7qnVrUeiXT8F3')
s.sendmail("studentscraper@gmail.com", "erickarschner@gmail.com", msg.as_string())

print(message)
