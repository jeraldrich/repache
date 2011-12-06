import re
import urllib2
import argparse
import threading
import Queue
import time

import mimetype_matches


request_queue = Queue.Queue()
log_data = []

class Repache(threading.Thread):
    def __init__(self, options, log_file_name='access.log'):
        self.log_line_regex = r'(?P<ip>[.:0-9a-fA-F]+) - - \[(?P<time>.*?)\] "GET (?P<uri>.*?) HTTP/1.\d" (?P<status_code>\d+) \d+ "(?P<referral>.*?)" "(?P<agent>.*?)"'
        try:
            self.log_file = open(log_file_name, 'r')
        except IOError:
            print "Error opening file %s" % (log_file_name)
            raise
        self.options = options
        # init local thread storage for parsed_log data sharing between threads
        threading.Thread.__init__(self)
        self.queue = request_queue

    def parse_log(self):
        """
        parse each line in the log and populate log data with matched pattern
        """
        global log_data
        # if log has already been parsed, do not parse file again
        if log_data:
            return True
        print "Parsing log..."
        search = re.compile(self.log_line_regex).search
        for line in self.log_file:
            if search(line):
                m = search(line)
                mimetype = self.determine_mimetype(m.group('uri'))
                log_data.append({
                         'mimetype': mimetype,
                         'server_ip': m.group('ip'),
                         'uri': m.group('uri'),
                         'time': m.group('time'),
                         'status_code': m.group('status_code'),
                         'referral': m.group('referral'),
                         'agent': m.group('agent')})
        return True

    def determine_mimetype(self, line_data):
        """
        determine mimetype by comparing passed line_data with mimetype_matches
        """
        for mimetype, mimetype_regex in mimetype_matches.matches.items():
            if mimetype_regex.match(line_data):
                return mimetype
        return "requests"

    def generate_mimetype_matches(self):
        """
        return dict of compiled regex matches and values for mimetypes
        """
        return {
                'image': re.compile(r'.*\.(?:png|jpg|jpeg|gif|tiff|svg|bmp|ico)'),
                'audio': re.compile(r'.*\.(?:mp3|aiff|m3u|wav|ram|mid|aif|snd)'),
                'application': re.compile(r'.*\.(?:pdf|xls|ogg)'),
                'video': re.compile(r'.*\.(?:mp2|mpa|mpe|mpeg|mpg|mpv2|mov|qt|avi|movie)'),
                'html': re.compile(r'.*\.(?:html|htm)'),
                'json': re.compile(r'.*\.(?:json)'),
                'javascript': re.compile(r'.*\.(?:javascript|js)'),
                'css': re.compile(r'.*\.(?:css)'),
                'xml': re.compile(r'.*\.(?:xml)')
              }

    def run(self):
        """
        send requests to server
        """
        while True:
            data = self.queue.get()
            if self.options.mimetype != '':
                if data['mimetype'] != self.options.mimetype:
                    return True
            request_str = ("%s%s" % (self.options.uri,
                                     data['uri']))
            try:
                print "sending request: %s" % (request_str)
                response = urllib2.urlopen((request_str), '',
                        int(self.options.request_timeout))
            except urllib2.HTTPError, e:
                print "The server could not fulfill the request"
                print "Status Code: %s" % (e.code)
            except urllib2.URLError, e:
                print "Failure to reach server"
                print "Reason: %s" % (e.reason)
            except Exception, e:
                print "General Exception: %s" % (request_str)
                print "%s" % (e)
            finally:
                self.queue.task_done()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', dest='filename',
                       help="path to apache access log file",
                       required=True)
    parser.add_argument('-u', '--uri', dest='uri', default='',
                       help="Base URI to send to.  If no URI is given, send\
                       requests to URL in parsed line of file")
    parser.add_argument('-m', '--mimetype', dest='mimetype', default='',
                       help="send requests of mimetype")
    parser.add_argument('-t', '--threads', dest='threads', default='1',
                       help="Amount of threads to spawn")
    parser.add_argument('-rt', '--request_timeout', dest='request_timeout', default='5',
                       help="Amount of time to wait on server response")
    args = parser.parse_args()

    # init pool of threads
    for i in range(int(args.threads)):
        repache = Repache(args)
        repache.parse_log()
        repache.setDaemon(True)
        repache.start()

    # populate thread queue
    for data in log_data:
        try:
            request_queue.put(data)
            time.sleep(0.5)
        except (KeyboardInterrupt, SystemExit):
            print 'Interrupt signal received'
            break

