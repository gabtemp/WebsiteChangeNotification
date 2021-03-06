import ConfigParser
import argparse
import difflib
import json
import smtplib
import urllib
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


def get_filename(url):
    url = url.replace('http://', '')
    url = url.replace('https://', '')
    url = url.replace('www.', '')
    url = url.replace('/', '_')
    url = url.replace('.', '_')
    return url + '_stored.html'


def read_html(path, filename):
    with open(path + '/' + filename, 'r') as f:
        return f.read()


def save_html(path, filename, text):
    with open(path + '/' + filename, 'w') as f:
        f.write(text)


def file_exists(path, filename):
    try:
        open(path + '/' + filename, 'r')
    except IOError:
        return False
    return True


def compare_html(expected, actual):
    lines1 = expected.splitlines(1)
    lines2 = actual.splitlines(1)
    if ''.join(difflib.context_diff(lines1, lines2)):
        print 'The HTML file changed since last check. Notifying via e-mail.'
        return True
    else:
        print "The HTML file didn't change since last check. Try again later."
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


# Command line arguments
parser = argparse.ArgumentParser(description='Monitor changes in websites.')
parser.add_argument('url', metavar='URL', type=str, help='the monitored url')
parser.add_argument('-p', '--params', metavar='params', type=json.loads,
                    help='optional url parameter for HTTP GET. In a JSON notation e.g.: \'{"foo" : "bar"}\'')

args = parser.parse_args()
url = args.url
params = args.params
####

# Configuration file options
config = ConfigParser.ConfigParser()
config.read('configuration.ini')

default_path = config.get('configuration', 'default_path')
recipient = config.get('configuration', 'recipient')
username = config.get('configuration', 'username')
password = config.get('configuration', 'password')
smtp_server = config.get('configuration', 'smtp_server')
####

current_html = get_html(url, params)
if not file_exists(default_path, get_filename(url)):
    print 'This is the first check on this website. From now on every change will be notified.'
    save_html(default_path, get_filename(url), current_html)
    exit(0)

print 'A previous version of this website was found. Comparing...'
last_html = read_html(default_path, get_filename(url))
different = compare_html(last_html, current_html)
if different:
    save_html(default_path, get_filename(url), current_html)
    notify(recipient, username, password, smtp_server, url)
