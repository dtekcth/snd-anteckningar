#!/usr/bin/env python
# coding: UTF-8
from email.parser import HeaderParser
import email
import imaplib
import os



def fetch_and_store():
     detach_dir = '.'
     m = imaplib.IMAP4_SSL("imap.gmail.com")
     m.login('dtekanteckningar@gmail.com','anteckningar')
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
         print (msg)
         mail = email.message_from_string(email_body) 
         temp = m.store(emailid,'+FLAGS', '\\Seen')
         m.expunge()

         if mail.get_content_maintype() != 'multipart':
             continue

         #print "["+mail["From"]+"] :" + mail["Subject"]

         #call("mkdir", data.
         for part in mail.walk():

             if part.get_content_maintype() == 'multipart':
                 continue
             if part.get('Content-Disposition') is None:
                 continue

             filename = part.get_filename()
             att_path = os.path.join(detach_dir, filename)

             if not os.path.isfile(att_path) :
                 fp = open(att_path, 'wb')
                 fp.write(part.get_payload(decode=True))
                 fp.close()


fetch_and_store()
