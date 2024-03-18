#!/usr/bin/python3.6
# -*- coding: iso-8859-15 -*-

## SSHD_CONFIG 
# Match group 2fa
#     ForceCommand /usr/bin/mailsec2fa.py
#
# create date : 01.02.2024
# created by  : Kemal Yildirim
# questions to : kemal.yildirim@outlook.com 


import datetime
import os
import socket
import logging
import sys 
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# VARIABLES
vers = "1.0.0"
start_date = datetime.datetime.now()
MONTH = start_date.strftime('%Y%m')
DAY = start_date.strftime('%Y%m%d')
username = os.getlogin()
mode="0"

conf_file ="/var/log/2fa/mailsec_access.db"
TMP_file="/var/log/2fa/templogin"
TMP_sec_code="/var/log/2fa/tempseccode"
LOG_PATH="/var/log/2fa/mailsec.log"


logging.basicConfig(filename=LOG_PATH,format='%(asctime)s %(levelname)s : %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)
if os.getpid():
    logging.info(f"Process id : {os.getpid()}")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def _read_file(file,usr):
    with open (file, "r") as myfile:
        data = [line for line in myfile if line.startswith(f"{usr}:")]
    return data

def _update_templogin(file,user,USR_tmp,last_date,day):
    search =(f"{user}:{last_date}") 
    replace = (f"{user}:{day}") 
    if not USR_tmp:
        with open (file, "a") as myfile:
            myfile.write(replace + '\n')
    else:
        with open (file, "r") as myfile:
            data = myfile.read()
            data = data.replace(search, replace)
        with open (file, "w") as myfile:
            myfile.write(data)
def _set_secCode():
    try:
        TMP_login_sec = _read_file(TMP_sec_code,username)
        last_login = TMP_login_sec[0].split(':',2)[1].strip()
        last_sec_code = TMP_login_sec[0].split(':',2)[2].strip()
        if last_login < DAY or last_login =="":
            sec_code = str(random.randint(0,999999))
            search =(f"{username}:{last_login}:{last_sec_code}") 
            replace = (f"{username}:{DAY}:{sec_code}") 
            with open (TMP_sec_code, "r") as myfile:
                data = myfile.read()
                data = data.replace(search, replace)
            with open (TMP_sec_code, "w") as myfile:
                myfile.write(data)
            return sec_code
        else:
            sec_code = TMP_login_sec[0].split(':',2)[2].strip()
            return sec_code
    except IndexError:
        sec_code = str(random.randint(0,999999))
        replace = (f"{username}:{DAY}:{sec_code}") 
        with open (TMP_sec_code, "a") as myfile:
            myfile.write(replace + '\n')
        return sec_code

def _sendMail(mail,sec_code):
    FROM ="no-reply@xxxx.com"
    SUBJECT =f" XXX Server Security Code :{sec_code}"
    message = """\
    
    Security Code : %s
        """ % (sec_code)
    try:
        msg = MIMEMultipart()
        msg['Subject'] = SUBJECT
        msg['From'] = FROM
        msg['To'] = mail
        msg.preamble = message
        body = MIMEText(message)
        msg.attach(body)
        # Send the mail with rely mail host 
        server = smtplib.SMTP("mail.smtp.xxxx")
        server.set_debuglevel(0)
        server.sendmail(FROM,mail,msg.as_string())
        logging.info("SendMail Successful...")
    except socket.error as e:
        logging.error("Could not connect to mail server : {0}".format(e))
    except:
        logging.error("Unknown error:", sys.exc_info()[0])
    finally:
        server.quit()

def main():
    err = 0
    logging.info(f"Login request from {username}")
    TMP_data = _read_file(conf_file,username)
    try:
        TMP_login = _read_file(TMP_file,username)
        USR_tmp= TMP_login[0].split(':',2)[0].strip()
        USR_last_login = TMP_login[0].split(':',2)[1].strip()
        logging.info(f"User Last Login Date : {USR_last_login}")
    except IndexError:
        USR_tmp=""
        USR_last_login=""
    sec_code = _set_secCode()
    try:
        USR_mail = TMP_data[0].split(':',3)[1]
        USR_Active = TMP_data[0].split(':',3)[2]
        if USR_Active == 0 or USR_Active <= DAY:
            logging.info(f"{username} is disabled or expired !!!")
            print(f"{username} is disabled or expired !!!  Please reach with admin team.")
            sys.exit() 
        if USR_last_login < DAY or USR_last_login =="":
            logging.info(f"Sec Code: {sec_code}")
            logging.info(f"User Mail : {USR_mail}")
            print(f"{bcolors.WARNING}You will receive an email about security code from no-reply@xxxxx.com in 1 min{bcolors.ENDC}")
            _sendMail(USR_mail,sec_code)
            while True:
                err +=1
                SEC_CODE_CHECK = input(f"{bcolors.OKGREEN}Security Code...: {bcolors.ENDC}")
                if SEC_CODE_CHECK == sec_code:
                    _update_templogin(TMP_file,username,USR_tmp,USR_last_login,DAY)
                    logging.info("Security code successful...")
                    break
                else:
                    print(f"{bcolors.FAIL}Wrong Security Code !!!{bcolors.ENDC}")
                    logging.error(f"{bcolors.FAIL}Wrong Security Code !!!{bcolors.ENDC}")
                if err >= 3: 
                    logging.error(f"{bcolors.FAIL}Wrong Security Code 3 times. exiting... !!!{bcolors.ENDC}")
                    sys.exit()
            logging.info("Success loggin with security code")
            os.system("exec ${SSH_ORIGINAL_COMMAND-$SHELL -l}; exec /bin/bash")
        else:
            logging.info("Success loggin because user has login date")
            os.system("exec ${SSH_ORIGINAL_COMMAND-$SHELL -l}; exec /bin/bash")
    except IndexError as err:
        print(f"{bcolors.WARNING} No username !!! Please reach with Admin Team{bcolors.ENDC}")
        logging.error(f"{bcolors.WARNING}No username in mailsec db !!!{bcolors.ENDC}")
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
    except EOFError:
        sys.exit()