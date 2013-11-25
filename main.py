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

def init_script():
    if not os.path.exists("uppladdat"):
        os.makedirs("uppladdat")
        os.makedirs("uppladdat/ERE102")
        os.makedirs("uppladdat/TIF085")
        os.makedirs("uppladdat/TMV216")
        os.makedirs("uppladdat/unsorted")
    else:
        if not os.path.exists("uppladdat/ERE102"):
            os.makedirs("uppladdat/ERE102")
        if not os.path.exists("uppladdat/TIF085"):
            os.makedirs("uppladdat/TIF085")
        if not os.path.exists("uppladdat/TMV216"):
            os.makedirs("uppladdat/TMV216")
        if not os.path.exists("uppladdat/unsorted"):
            os.makedirs("uppladdat/unsorted")

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

        if not parseSubLine(subjectline) :             #Ifall mailet har fel rubrik, går vi in här
           print "send mail"
           # sendEmail(name, fromaddr, subjectline)      #Skickar ett mail till avsändaren om att dens mail haft fel format på rubriken
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
            
            dirs = os.listdir(format(subjectline))
            subdir = "unsorted"
            if (subjectline.startswith("ERE102-") or subjectline.startswith("TIF085-") or subjectline.startswith("TMV216-")) :
               subdir = subjectline[:6]
            if dirs[0].endswith(".jpg") :
               call(["convert"] + glob.glob(subjectline + "/*") + ["uppladdat/" + subdir + "/{0}.pdf".format(subjectline)])
               shutil.rmtree(subjectline)
            elif dirs[0].endswith(".pdf") and len(dirs) == 1 :
               path = subjectline + "/" + dirs[0]
               dest = "uppladdat/" + subdir + "/{0}.pdf".format(subjectline)
               shutil.move(path,dest)
               shutil.rmtree(subjectline)
            #elif dirs[0].endswith(".pdf") :
               #print ["pdftk"] + glob.glob(subjectline + "/*") + ["cat output uppladdat/" + "{0}.pdf".format(subjectline)]
               #call(["pdftk"] + glob.glob(subjectline + "/*") + ["cat output uppladdat/" + "{0}.pdf".format(subjectline)])
               #shutil.rmtree(subjectline) #Hämtar alla attechments, sätter ihop de till en .pdf

def createHTML():
    uppladdat = os.listdir("uppladdat")
    f = open("index.html", "w")
    f.write('<html><head><title>Anteckningar Dtek</title><meta charset="UTF-8"><link href="mall.css" rel="stylesheet" media="all"></head><body>')
    f.write('<div class="flex-container flex-container-style fixed-height">')
    f.write('<div class="flex-item"><h1> Reglerteknik </h1><ul id="ERE102">')
    for fil in os.listdir("uppladdat/ERE102") :
        if(fil.endswith(".pdf")) :
            f.write('<li><a href="uppladdat/ERE102/{0}">{1}</a></li>'.format(fil,fil[7:]))
    f.write('</ul></div>')
    f.write('<div class="flex-item"><h1> Fysik för ingenjörer</h1><ul id="TIF085"> ')
    for fil in os.listdir("uppladdat/TIF085") :
        if(fil.endswith(".pdf")) :
            f.write('<li><a href="uppladdat/TIF085/{0}">{1}</a></li>'.format(fil,fil[7:]))
    f.write('</ul></div>')
    f.write('<div class="flex-item"> <h1> Linjär algebra</h1><ul id="TMV216">')
    for fil in os.listdir("uppladdat/TMV216") :
        if(fil.endswith(".pdf")) :
            f.write('<li><a href="uppladdat/TMV216/{0}">{1}</a></li>'.format(fil,fil[7:]))
    f.write('</ul></div></div>')
    f.write('<div class="disc"><a href="http://snd.dtek.se"><img src="http://snd.dtek.se/wp-content/uploads/2013/02/sndlogga.png"></a>')
    f.write('<div class="discText"> Disclaimer: På denna sidan samlas anteckningar gjorda av Teknologer på D-sektionen. Vi i SND kan ej garantera att anteckningarna stämmer.</div>')
    f.write('<div class="discText"> Uppdaterad: ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + '</div></div>')
    f.write('</body></html>') #Bygger html-sidan

def parseSubLine(string): #Parsar rubriken, kollar om det är rätt format
    splitted = string.split("-")
    if not (len(splitted) == 5 or len(splitted) == 6):
        return False
    if (re.match("[A-Za-z]", splitted[0][:3]) and re.match("[0-9]", splitted[0][-3:])):
        if (re.match("[0-9]",splitted[1]) and re.match("[0-9]",splitted[2]) and re.match("[0-9]",splitted[3])):
            return True
    return False

def sendEmail(name,toaddrs,subjectline): # Skickar ett mail
    fromaddr = 'dtekanteckningar@gmail.com'
    msg = 'Hej ' + name +'\n \n Det mail du har skickat med rubriken ' + subjectline + ' har fel format. Formatet är ERE102-2013-MM-DD-CID. Vänligen skicka ett nytt mail.\n\n MVH SND' 
    sub = "Uppladdning av dina anteckingar gick fel"
 
    username = 'dtekanteckningar'  
      
    server = smtplib.SMTP('smtp.gmail.com:587')  
    server.starttls()  
    server.login(username,getPassword()) 
    message = 'Subject: %s\n\n%s' % (sub, msg) 
    server.sendmail(fromaddr, toaddrs, message)  
    server.quit()  

def getPassword():
    password = ""
    f = open('password.txt', 'r')
    try:
        password = f.read()
    finally:
        f.close()
    return base64.b64decode(password) #Hämtar lösenordet till gmail-kontot


#### Här Börjar Programet ####
init_script()
fetch_and_store()
createHTML()
