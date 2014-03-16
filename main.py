#!/usr/bin/env python
# coding: UTF-8
from email.parser import HeaderParser
from subprocess import call
import email
import imaplib
import smtplib
import os
import re
import string
import glob
import shutil
import base64
from time import gmtime, strftime


#Creates a dir for every course in sender.txt
def init_script():
    f = open('sender.txt')
    lines = f.readlines()
    f.close()
    for emailAddress in lines :
        splitted = re.split(r'\s+', emailAddress.rstrip('\t\n'))
        if not splitted[0][:1] == '#' :
            if not os.path.exists("www/uppladdat/{0}".format(splitted[1])):
                os.makedirs("www/uppladdat/{0}".format(splitted[1]))

#Fetches the email attachment, and complise multiple .jpg's to a .pdf
def fetch_and_store():
    detach_dir = '.'
    m = imaplib.IMAP4_SSL("imap.gmail.com")
    m.login('dtekanteckningar@gmail.com',getPassword())
    m.select("inbox")

    resp, items = m.search(None, "(UNSEEN)")
    items = items[0].split()

    for emailid in items:
        resp, data = m.fetch(emailid, "(RFC822)") 
        email_body = data[0][1] 
        resp2, header = m.fetch(emailid, '(BODY[HEADER.FIELDS (SUBJECT)])')
        subject = header[0][1]
        parser = HeaderParser()
        msg = parser.parsestr(subject)
        subjectline = "".join(re.findall(r'[0-9a-zA-Z\-]', msg["Subject"]))

        mail = email.message_from_string(email_body)
        from email.utils import parseaddr
        fromaddr = parseaddr(mail['from'])[1]
        name = parseaddr(mail['from'])[0]
        temp = m.store(emailid,'+FLAGS', '\\Seen')
        m.expunge()

        if not parseSubLine(subjectline) and checkSender(fromaddr) :             #Ifall mailet har fel rubrik, går vi in här
            if not parseSubLine(subjectline) :
                print "wrong subjectline"
                sendEmail(name, fromaddr, subjectline, "2")
            elif not checkSender(fromaddr) :
                print "address does not exists"
                sendEmail(name, fromaddr, subjectline, "1")      #Skickar ett mail till avsändaren om att dens mail haft fel format på rubriken
            print checkSender(fromaddr)
        else:
            if not os.path.exists(subjectline):
                os.makedirs(subjectline)

            if mail.get_content_maintype() != 'multipart':
                continue

            filenamelist = []
            for part in mail.walk():

                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                                   
                filename = "".join(re.findall(r'[.0-9a-zA-Z\-]',part.get_filename()))                 
                att_path = os.path.join(detach_dir + "/" + subjectline, filename)
                filenamelist.append(filename)
                if not os.path.isfile(att_path) :
                    fp = open(att_path, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
            
            var = checkSender(fromaddr)
            course = var[0]
            name = var[1]
            dest = "www/uppladdat/" + course + "/{0}.pdf".format(setFileName(name,subjectline))
            dirs = os.listdir(format(subjectline))
            if dirs[0].endswith(".jpg") :
               call(["convert"] + glob.glob(subjectline + "/*") + [dest])
               shutil.rmtree(subjectline)
            elif dirs[0].endswith(".pdf") and len(dirs) == 1 :
               path = subjectline + "/" + dirs[0]
               shutil.move(path,dest)
               shutil.rmtree(subjectline)

# Creates a HTML-Page
def createHTML():
    f = open("www/index.html", "w")
    f.write('<html><head><title>Anteckningar Dtek</title><meta charset="UTF-8"><link href="mall.css" rel="stylesheet" media="all"></head><body>')
    f.write('<div class="flex-container flex-container-style fixed-height">')
    f.write( listFileHTML() )
    f.write('</div>')
    f.write('<div class="disc"><a href="http://snd.dtek.se"><img src="http://snd.dtek.se/wp-content/uploads/2013/02/sndlogga.png"></a>')
    f.write('<div class="discText"> Disclaimer: På denna sidan samlas anteckningar gjorda av Teknologer på D-sektionen. Vi i SND kan ej garantera att anteckningarna stämmer.</div>')
    f.write('<div class="discText"> Uppdaterad: ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + '</div></div>')
    f.write('</body></html>') #Bygger html-sidan

def listFileHTML():
    string = ""
    for dir in sortDir(os.listdir("www/uppladdat")):
        if os.path.isdir("www/uppladdat/{0}".format(dir)):
            string += str('<div class="flex-item"><h1>{0}</h1><ul id="{0}">'.format(dir))
            for fil in sortDir(os.listdir("www/uppladdat/{0}".format(dir))) :
                if fil.endswith(".pdf") :
                    string += str('<li><a href="uppladdat/{0}/{1}">{2}</a></li>'.format(fil[:6],fil,fil[7:]))
            string += str('</ul></div>')
    return string

def checkSender(string) :
    f = open('sender.txt')
    lines = f.readlines()
    f.close()
    for emailAddress in lines :
        splitted = re.split(r'\t+', emailAddress.rstrip('\t\n'))
        if not splitted[0] == '#' :
            if splitted[0] == string:
                return splitted[1:]
    return False

def sortDir(dir) :
    return sorted(dir, key=lambda x: x.split('-')[1:4])

def parseSubLine(string):
    splitted = string.split("-")
    if not (len(splitted) == 2 or len(splitted) == 3):
        return False
    if len(splitted[0]) > 2 or len(splitted[1]) > 2 :
        return False
    if re.match("[0-9]",splitted[0]) and re.match("[0-9]",splitted[1]) :
        return True
    return False

def setFileName(name,subjectline) :
    splitted = subjectline.split("-")
    year = strftime("%Y", gmtime())
    date = "{0}-{1}".format(splitted[0],splitted[1])
    info = ""
    if len(splitted) > 2:
        info = "-{0}".format(splitted[2])
    return "EEM076-{0}-{1}-{2}{3}".format(year,date,name,info)

# Skickar ett mail om
def sendEmail(name,toaddrs,subjectline,error): 
    fromaddr = 'dtekanteckningar@gmail.com'
    if error == "1" :
        errorMsg = "Detta beror på att denna mail ej är registrerad som antecknare. Hör av dig till snd@dtek.se så fixar dem det."
    elif error == "2" :
        errorMsg = "Rubriken: {0} på ditt mail har fel format. Formatet skall vara MM-DD exempel 03-12 för 12 Mars. Skicka ett nytt mail med rätt rubrik :)".format(subjectline)
    msg = 'Hej {0}\n\n Uppladdningen av dina antecknignar gick fel.\n{1}\n\n MVH SND'.format(name,errorMsg) 
    sub = "Uppladdning av dina anteckingar gick fel"
 
    username = 'dtekanteckningar'  
      
    server = smtplib.SMTP('smtp.gmail.com:587')  
    server.starttls()  
    server.login(username,getPassword()) 
    message = 'Subject: %s\n\n%s' % (sub, msg) 
    server.sendmail(fromaddr, toaddrs, message)  
    server.quit()  

#Hämtar lösenordet till gmail-kontot
def getPassword():
    password = ""
    f = open('password.txt', 'r')
    try:
        password = f.read()
    finally:
        f.close()
    return base64.b64decode(password) 


#### Här Börjar Programet ####
init_script()
fetch_and_store()
createHTML()
