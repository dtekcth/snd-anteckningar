#!/usr/bin/env python
# coding: latin-1
from pyPdf import PdfFileWriter, PdfFileReader
import email
import imaplib

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('dtekanteckningar@gmail.com', 'anteckningar')
mail.list()
# Out: list of "folders" aka labels in gmail.
mail.select("inbox") # connect to inbox.

result, data = mail.search(None, "ALL")
 
ids = data[0] # data is a list.
id_list = ids.split() # ids is a space separated string
latest_email_id = id_list[-1] # get the latest
 
result, data = mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822) for the given ID
 
email_body = data[0][1] # here's the body, which is raw text of the whole email
# including headers and alternate payloads

mail = email.message_from_string(email_body)

f = open('testmail', 'w+')
#f.write(mail) #inte moget än
f.write(email_body)

#print(mail)

###################
#http://stackoverflow.com/questions/6225763/downloading-multiple-attachments-using-imaplib
###################