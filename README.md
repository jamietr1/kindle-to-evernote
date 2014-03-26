kindle-to-evernote
==================
This Python script will read and parse the "My Clippings.txt" file on Kindle device, organize
them into title-based notes for Evernote and then email the results to Evernote using the append
option to append to existing notes.

Requires the following Python packages:
- six-1.5.2
- python-dateutil-2.2

To install using ``pip``:

    pip install -r requirements.txt

See the following post for more details on how this work: http://www.jamierubin.net/2014/03/11/going-paperless-quick-tip-append-to-existing-notes-in-evernote-via-email/


NOTES ABOUT EVERNOTE EMAIL LIMITS.

This script uses the email-to-Evernote functionality to update your Kindle notes in Evernote. It sends one note per title for which an update is required each time it runs. If you have a lot of highlights over a lot of different titles, be aware of these daily limits for emailing to Evernote accounts:

- Free: 50 daily
- Premium: 250 daily
- Business: 250 daily

More information about Evernote account limits can be found here: http://evernote.com/contact/support/kb/#!/article/23283158

THIS IS CURRENTLY UNDER CONSTRUCTION.
