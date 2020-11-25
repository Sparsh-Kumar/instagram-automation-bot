

import time
import logging
import sys
import datetime
import os
import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from bs4 import BeautifulSoup
import random

INSTAGRAM_USERNAME = 'YOUR INSTAGRAM USERNAME'
INSTAGRAM_PASSWORD = 'YOUR INSTAGRAM PASSWORD'
FILENAME = ''
HASHTAG = 'NAME OF THE HASHTAG'
COMMENT = ''
TIMES = 45
follow = None
like = None
comment = None

class Hashtag:

	def __init__ (self, webdriverpath = None):
		if not webdriverpath:
			webdriverpath = os.path.join (Path.home (), 'Desktop', 'chromedriver.exe')
		self.__webdriverpath = webdriverpath
		self.__driver = None
		self.__logger = None
		self.__baseURI = 'https://www.instagram.com/explore/tags/' + HASHTAG
		self.enableLogging ()

	def enableLogging (self):
		logging.basicConfig (filename = 'logsfile.log', format='%(asctime)s %(message)s', filemode = 'w')
		self.__logger = logging.getLogger ()
		self.__logger.setLevel (logging.DEBUG)

	def getField (self, xpath = None):
		try:
			field = WebDriverWait (self.__driver, 30).until (EC.presence_of_element_located ((By.XPATH, xpath)))
			return field
		except Exception as e:
			self.__logger.error (e)
			self.closeBot ()
			sys.exit (2)

	def startLogin (self):
		try:
			firstpic = self.getField ('/html/body/div[1]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div')
			firstpic.click ()
			usernamefield = self.getField ('/html/body/div[5]/div[2]/div/div[2]/div/div/div[1]/div/form/div[1]/div[1]/div/label/input')
			usernamefield.send_keys (INSTAGRAM_USERNAME)
			passwordfield = self.getField ('/html/body/div[5]/div[2]/div/div[2]/div/div/div[1]/div/form/div[1]/div[2]/div/label/input')
			passwordfield.send_keys (INSTAGRAM_PASSWORD)
			loginButton = self.getField ('/html/body/div[5]/div[2]/div/div[2]/div/div/div[1]/div/form/div[1]/div[3]/button/div')
			loginButton.click ()
			notnowButton = self.getField ('/html/body/div[1]/section/main/div/div/div/div/button')
			notnowButton.click ()
		except Exception as e:
			self.__logger.error (e)
			self.closeBot ()
			sys.exit (4)

	def getInstagramName (self):
		try:
			instagramName = self.getField ('/html/body/div[5]/div[2]/div/article/header/div[2]/div[1]/div[1]/span/a')
			instagramName = 'https://instagram.com/' + instagramName.text
			return instagramName
		except Exception as e:
			self.__logger.error (e)
			self.closeBot ()
			sys.exit (6)

	def startInteracting (self):
		try:
			firstpic = self.getField ('/html/body/div[1]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div')
			firstpic.click ()
			counter = 1;
			while counter < TIMES:
				instagramName = self.getInstagramName ()
				f = open (os.path.join (os.getcwd (), 'campaign', FILENAME), 'r+')
				allNames = f.read ().split ('\n')
				nextbutton = WebDriverWait (self.__driver, 15).until (EC.presence_of_element_located ((By.LINK_TEXT, 'Next')))
				if instagramName in allNames:
					nextbutton.click ()
				else:
					if follow:
						time.sleep (random.randint (2, 4))
						followbutton = self.getField ('/html/body/div[5]/div[2]/div/article/header/div[2]/div[1]/div[2]/button')
						followbutton.click ()
						time.sleep (random.randint (2, 7))
					if comment:
						time.sleep (random.randint (2, 4))
						commentbutton = self.getField ('/html/body/div[5]/div[2]/div/article/div[3]/section[1]/span[2]/button/div')
						commentbutton.click ()
						commentarea = WebDriverWait (self.__driver, 15).until (EC.presence_of_element_located ((By.CLASS_NAME, 'Ypffh')))
						commentarea.send_keys (COMMENT)
						commentarea.send_keys (Keys.ENTER)
						time.sleep (random.randint (2, 7))
					if like:
						time.sleep (random.randint (2, 4))
						likebutton = WebDriverWait (self.__driver, 15).until (EC.presence_of_element_located ((By.CLASS_NAME, 'fr66n')))
						soup = BeautifulSoup (likebutton.get_attribute ('innerHTML'), 'html.parser')
						if (soup.find ('svg') ['aria-label'] == 'Like'):
							likebutton.click ()
						time.sleep (random.randint (2, 7))
					f.write (instagramName + '\n')
					f.close ()
					nextbutton.click ()
					counter = counter + 1 # Only increase the counter if and only if a new person is liked or followed  
		except Exception as e:
			self.__logger.error (e)
			self.closeBot ()
			sys.exit (5)

	def getURI (self):
		try:
			self.__driver = webdriver.Chrome (self.__webdriverpath)
			#self.__driver.maximize_window ()
			self.__driver.get (self.__baseURI)
			self.__logger.debug ('[*] Done opening the hashtagURI' + self.__baseURI)
		except Exception as e:
			self.__logger.error (e)
			self.closeBot ()
			sys.exit (3)

	def closeBot (self):
		self.__logger.debug ('[*] Shutting down the webdriver code ....')
		self.__driver.quit ()

	def __del__ (self):
		pass;

if __name__ == '__main__':

	parser = argparse.ArgumentParser (description = 'like comment and follow latest hashtags automatically')
	parser.add_argument ('--follow', action = 'store', dest = 'follow', type=int, required = False, help = 'enable your bot to follow people')
	parser.add_argument ('--like', action = 'store', dest = 'like', type=int, required = False, help = 'enable your bot to like people pics')
	parser.add_argument ('--comment', action = 'store', dest = 'comment', type=int, required = False, help = 'enable your bot to comment on people pics')
	given_args = parser.parse_args ()
	
	follow = given_args.follow
	like = given_args.like
	comment = given_args.comment

	if follow:
		FILENAME = FILENAME + 'Followed-'
	if like:
		FILENAME = FILENAME + 'liked-'
	if comment:
		FILENAME = FILENAME + 'Commented-'
	currentTime = datetime.datetime.now ().strftime ("%Y-%m-%d-%H-%M-%S")
	FILENAME = FILENAME + currentTime + '.txt'

	if not os.path.exists ('campaign'):
		os.makedirs ('campaign')

	if not follow and not like and not comment:
		sys.stderr.write ('[-] please enter at least one operation\n')
		sys.stderr.write ('[-] Exiting ....\n')
		sys.stderr.flush ()
		sys.exit (6)

	try:
		f = open (os.path.join (os.getcwd (), 'campaign', FILENAME), 'w')
		f.close ()
	except Exception as e:
		print (e)
		sys.exit (20)

	hashtag = Hashtag ()
	hashtag.getURI ()
	time.sleep (5)
	hashtag.startLogin ()
	hashtag.startInteracting ()
	hashtag.closeBot ()