import time
import openai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GmailAutomation:
    def __init__(self, api_key, email, password, senderName):
        self.api_key = api_key
        self.email = email
        self.password = password
        self.senderName = senderName

    def login(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.driver.maximize_window()
        self.driver.delete_all_cookies()
        self.driver.get('https://mail.google.com/')
        time.sleep(2)

        self.driver.find_element(By.ID, 'identifierId').send_keys(self.email)
        self.driver.find_element(By.ID, 'identifierNext').click()
        time.sleep(2)

        password_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.NAME, 'Passwd')))
        password_field.send_keys(self.password)
        time.sleep(3)

        next_button_after_password = WebDriverWait(self.driver, 10).until(
         EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
        next_button_after_password.click()

    def move_emails_from_spam_to_inbox(self):
        time.sleep(10)
        menu_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='gb_Nc']"))
        )
        sidebar_expanded = menu_button.get_attribute("aria-expanded")
        if sidebar_expanded == 'false':
            menu_button.click() 

        print('Opening more options')  

        more_button = WebDriverWait(self.driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='G-asx J-J5-Ji']"))
        )
        more_button.click()
        time.sleep(3) 

        print('Moving to spam folder')
        time.sleep(2)

        spam_button = WebDriverWait(self.driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@aria-label, 'Spam')]"))
        )
        spam_button.click()  

        print("Opened spam folder")

        try:
            no_spam_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//td[@class='TC' and text()='Hooray, no spam here!']")))        
            print("No spam found in the spam folder.")
            return
        except:
            print("Found spammed emails")
            
        select_all_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div[3]/div/div[2]/div[4]/div/div/div/div[1]/div[2]/div[2]/div[1]/div/div/div[1]/div/div[1]/span"))
        )
        
        print("Selecting all emails")
        select_all_button.click()
        print("Selected all emails")
        time.sleep(5)

        not_spam_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='Bn' and contains(text(), 'Not spam')]"))
         )
        not_spam_button.click()
        print("Moved emails from spam to inbox")
        time.sleep(5)  

    def reply_to_emails(self):
        time.sleep(2)
        self.driver.get('https://mail.google.com/mail/u/0/#inbox')
        time.sleep(5)

        unread_emails = self.driver.find_elements(By.XPATH, "//tr[@class='zA zE']")
        for email in unread_emails:
            email.click()
    
            time.sleep(5)
            email_body = self.driver.find_element(By.CSS_SELECTOR, 'div.adn.ads').text
            
            reply = self.ai_responder(email_body)

            reply_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='T-I J-J5-Ji T-I-Js-IF aaq T-I-ax7 L3']")))
                      
            reply_button.click()
            time.sleep(3)
            
            reply_textarea =  WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@class='Am aiL aO9 Al editable LW-avf tS-tW']")))
            reply_textarea.send_keys(reply)
            time.sleep(3) 

            send_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='T-I J-J5-Ji aoO v7 T-I-atl L3']")))
            send_button.click()

            time.sleep(2)
            self.driver.get('https://mail.google.com/mail/u/0/#inbox')
            print('Message sent successfully')

    def ai_responder(self, message):
        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"Reply to the following email and here is my name: {self.senderName}" + str(message)
                    }
                ],
                temperature=0.8,
                max_tokens=200
            )
            return response.choices[0].message.content
        except openai.Error as e:
            print("Error:", e)
            return "Error: Maximum tokens exceeded. Please try again with a shorter input."

    def close_browser(self):
        time.sleep(5)
        self.driver.quit()
        

if __name__ == "__main__":
    api_key = "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"
    email = "yohannes.ahunm@aait.edu.et"
    password = "Yony!!33!!"
    senderName = 'Yohannes'

    gmail_automation = GmailAutomation(api_key, email, password, senderName)
    gmail_automation.login()
    gmail_automation.move_emails_from_spam_to_inbox()
    gmail_automation.reply_to_emails()
    gmail_automation.close_browser()
    print("Email automation completed.")
