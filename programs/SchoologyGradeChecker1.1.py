# originally created on Thu Dec 31, 2020 by John Exterkamp
# this program reads the grades from schoology
# Made from Dec 31 3:00pm to Jan 26 8:22 2021
#from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyautogui
from gtts import gTTS
from playsound import playsound
import os
import speech_recognition as sr


# I learned from this program:
# Inspect element provides coping Xpaths
# Xpaths
# Xpaths can be shortend
# more about html and id tags
# selenium
# f'' formatting only works in 3.7 and above

# I need homebrew




def getCourseGrades(email='', password='',sayGrade=False, alertGrade=True):
    grades = {}
    #
    print(email + password)

    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-notifications')

    path = b'C:\Users\kaura\Desktop\chromedriver.exe'
    driver = webdriver.Chrome(path, options=chrome_options)

    driver.get('https://fortthomas.schoology.com/home/recent-activity')

    # useful tip I found when chrome asks for something
    # alert_obj = driver.switch_to.alert
    # alert_obj.accept()

    # driver.page_source = full page html
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "i0116"))
    )
    element.send_keys(email)
    element.send_keys(Keys.RETURN)

    element = WebDriverWait(driver, 10).until(                           #  this line of code waits until the element appears in the driver
        EC.presence_of_element_located((By.ID, "i0118"))
    )
    time.sleep(1)
    passwordInput = driver.find_element_by_id("i0118")
    passwordInput.send_keys(password)
    passwordInput.send_keys(Keys.RETURN)

    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "idSIButton9"))
    )
    element.click()

    # up coming events code
    time.sleep(1)

    #upcomingList = driver.find_elements_by_xpath('//div[@class="upcoming-events upcoming-events-wrapper sEventUpcoming-processed"]//div[@class="upcoming-list"]')
    #for i in range(len(upcomingList)):


    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[@href="/grades/grades"]'))
    )
    element.click()

    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="gradebook-course hierarchical-grading-report show-title interactive sGradesGradebook-processed sGradeHierarchicalReport-processed"]'))
    )

    classes = driver.find_elements_by_xpath('//div[@class="gradebook-course hierarchical-grading-report show-title interactive sGradesGradebook-processed sGradeHierarchicalReport-processed"]') #  overarching class div
    # classTitles = driver.find_elements_by_xpath('//a[@class="sExtlink-processed"][@href="#"]')  #  TIP: this is how you list multiple atributes in xpath you use //<name>[@<name>="value"][repeat]  title for the class
    # secondaryCourseGrades = driver.find_elements_by_xpath('//span[@class="course-grade-value"]//span[@class="awarded-grade"]//span[@class="numeric-grade secondary-grade"]//span[@class="rounded-grade"]')  # super cool thing I found xpath is stackable with order from parent --> child
    # primaryCourseGrades = driver.find_elements_by_xpath('//span[@class="course-grade-value"]//span[@class="awarded-grade"]//span[@class="numeric-grade primary-grade"]//span[@class="rounded-grade"]')
    # noGrades = driver.find_elements_by_xpath('//span[@class="course-grade-value"]//span[@class="no-grade"]')

    # print(len(classes))
    # print(len(classTitles))
    classTitles = []

    for i in range(len(classes)):

        classId = classes[i].get_attribute('id')                                                                                          
        # this was quite a long process figuring out a way to get each classes grade. first, I scraped the webpage and found all of the grades. I tried to link them all by running multiple
        # lists and commparing the idex of each one in a for loop but quickly found it wouldent corrispond
        # I looked and looked until i relized each class has an id and went from there.
        classTitle = driver.find_element_by_xpath(f'//div[@id="{classId}"]//a[@class="sExtlink-processed"][@href="#"]').text
        classTitles.append(classTitle)

        while True:
            try:
                # first it sees if the course grade says N/A

                noGrade = driver.find_element_by_xpath(f'//*[@id="{classId}"]/div[2]/div/div/span[2]/span[@class="no-grade"]')
                grade = 'N/A'
                print(grade + ' | ' + classTitle)
                grades.update({classTitle : grade})
                break # if true and it makes through without errors it exits the while loop
            except:
                pass
            try:
                # tries to get grades with numbers as seconddary value becuase some grades have letter and num grades

                secondaryCourseGrade = driver.find_element_by_xpath(f'//*[@id="{classId}"]/div[2]/div/div/span[2]/span/span[2]/span') # as you can see I just figured out you can copy shortend Xpaths!
                grade = secondaryCourseGrade.get_attribute('title')      # you can get any atrribute value with this function
                print(grade + ' | ' + classTitle)
                grades.update({classTitle : grade})
                break
            except Exception as ex:
                pass
            try:
                # for regular classes with just number course grades

                primaryCourseGrade = driver.find_element_by_xpath(f'//*[@id="{classId}"]/div[2]/div/div/span[2]/span/span/span')
                grade = primaryCourseGrade.get_attribute('title')
                print(grade + ' | ' + classTitle)
                grades.update({classTitle : grade})
                break
            except Exception as ex:
                pass
            try:
                qg = []
                # classes with no course grades... I just now relized this one fuction could do all the classes... ughh

                # driver.find_elements_by_xpath(//[@id="{classId}"]/div[@class="gradebook-course-title"]/
                qGradeList = driver.find_elements_by_xpath(f'//div[@id="{classId}"]//tr[@class="report-row period-row has-children childrenCollapsed"]//span[@class="rounded-grade"]') 
                #this was fun to figure out I once again tried to get the xpath and relized there is alot of the same elements with the tr tag so I looked at them closely for a while.
                # then relized the ones showing on the page didn't have hidden in the class name so if i have an xpath with the regular class id and then the class whala i get a list
                # of elements with the showing tag!
                # then i run a for loop on the list and add the vals then divide by the list length

                qnum = len(qGradeList)
                grade = 0

                for i in range(len(qGradeList)):
                    qgrade = qGradeList[i].get_attribute('title')
                    qgrade = qgrade.replace('%', '')
                    grade = float(qgrade) + float(grade)
                grade = grade / len(qGradeList)
                print(str(grade) + '% | ' + classTitle)
                grades.update({classTitle : str(grade)})
                break
            except Exception as Ex:
                pass

    driver.quit()

    if alertGrade:
        print('\n')
        alertString = ''
        for i in range(len(classes)):
            classTitle = classTitles[i].split(':')[0]
            if grades[classTitles[i]].split('%')[0] != 'N/A':
                alertString = alertString + classTitle + ' == '  + str(round(float(grades[classTitles[i]].split('%')[0]), 2)) + '\n'
            else:
                alertString = alertString + classTitle + ' == '  + grades[classTitles[i]] + '\n'


        pyautogui.alert(text=alertString, title="Grades", button="OK")

    if sayGrade:
        sayString = ''
        for i in range(len(classes)):
            classTitle = classTitles[i].split(' ')[0]
            if grades[classTitles[i]].split('%')[0] != 'N/A':
                sayString = f' your average grade for {classTitle} is, ' + str(round(float(grades[classTitles[i]].split('%')[0]), 2)) + ' percent.' + sayString
            else:
                sayString = f'your average grade for {classTitle} is, {grades[classTitles[i]]}.' + sayString
            pass
        tts = gTTS(sayString)
        tts.save('alert.mp3')
        playsound('alert.mp3')

while True:
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            audio = r.listen(source, timeout=1)
            text = r.recognize_google(audio)
            print(text)
            if 'grade' in text:
                print(text + ' top')
                tts = gTTS('Okay!')
                tts.save('message.mp3')
                playsound('message.mp3')
                getCourseGrades(sayGrade=True, alertGrade=False)
            if 'quit' in text:
                print(text + ' bottom')
                tts = gTTS('Quiting!')
                tts.save('message.mp3')
                playsound('message.mp3')
                break
    except:
        pass
