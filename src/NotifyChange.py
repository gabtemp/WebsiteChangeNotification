import urllib
import difflib
import smtplib
from email.mime.text import MIMEText


def get_html(url, params=None):
    if params:
        url = url + '?' + urllib.urlencode(params)

    print 'Attempting HTTP GET on ' + url
    response = urllib.urlopen(url)
    if response.code == 200:
        print 'Got response code 200!'
        return response.read()
    else:
        print 'Error, response code: ' + response.code + '.'


def compare_html(expected, actual):
    lines1 = expected.splitlines(1)
    lines2 = actual.splitlines(1)
    if ''.join(difflib.context_diff(lines1, lines2)):
        print 'The HTML file changed since last check. Notifying via e-mail.'
        return True
    else:
        print "The HTML file didn't change since last check. Trying again later."
        return False


def notify(recipient, username, password, smtp_server, url):
    message = MIMEText('The site you were monitoring changed!\n\r'
                       'Here is the link to the page: ' + url)

    message['Subject'] = 'Website update!'
    message['From'] = username
    message['To'] = recipient

    # Considering an TLS connection
    print 'Sending email on ' + smtp_server + ' with user ' + username
    smtp = smtplib.SMTP(smtp_server)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(username, [recipient], message.as_string())
    smtp.quit()
    print 'Email sent successfully'
