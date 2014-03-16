snd-anteckningar by Johan Bowald
================

Python script that fetches jpg's or a pdf from a mail server and merges every containing several jpgs to a pdf/mail.

========================= SET UP =========================

sender.txt contains the contributers.
They are the ony ones that are able to upload files via email.

password.txt
should contain the base64 encryption of your password

========================= RUNNING DETAILS =========================
You'll need Imagemagick and python

Imagemagick download: http://www.imagemagick.org/script/index.php

The script will first set up the folder structure needed.
Then Download the attachments, compress them to a .pdf and place in "www/uppladdat" directory.

When all new emails are downloaded, an .html-file will be created with links to every downloaded file. Sorted by the course-code specified in sender.txt

========================= TODO! =========================

Need a new design on the HTML page. The boxes needs to expand downwards or a menu would need to be added. And only show one box at the time

Add Connection constants, so any email can be used without changing the python file.

========================= Bugs! =========================

The scipt does not send an email to people that isn't in the sender.txt list