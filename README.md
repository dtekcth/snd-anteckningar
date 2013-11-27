snd-anteckningar
================

Python script that fetches jpg's or a pdf from a mail server and merges every containing several jpgs to a pdf/mail.


========================= RUNNING DETAILS =========================
The script is design to work with the courses ERE102, TMV216 and TDA

You'll need Imagemagick and python

Imagemagick download: http://www.imagemagick.org/script/index.php

The scrippt will first set up the folder structure needed.
Then Download the attachments, compress them to a .pdf and place in "uppladdat" directory.

When all new emails are downloaded, an .html-file will be created with links to every downloaded file.