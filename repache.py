import re
import urllib2
import argparse


class Repache:
    def __init__(self, options, log_file_name='access.log'):
        self.log_line_regex = r'(?P<ip>[.:0-9a-fA-F]+) - - \[(?P<time>.*?)\] "GET (?P<uri>.*?) HTTP/1.\d" (?P<status_code>\d+) \d+ "(?P<referral>.*?)" "(?P<agent>.*?)"'
        try:
            self.log_file = open(log_file_name, 'r')
        except IOError:
            print "Error opening file %s"%(log_file_name)
            raise
        self.log_data = []
        self.log_file_name = options.filename_opt
        self.uri = options.uri_opt
        self.mimetype_matches = self.generate_mimetype_matches()


    def parse_log(self):
        """
        parse each line in the log and populate log data with matched pattern
        """
        search = re.compile(self.log_line_regex).search
        for line in self.log_file:
            if search(line):
                m = search(line)
                mimetype = self.determine_mimetype(m.group('uri'))
                self.log_data.append({
                         'mimetype': mimetype,
                         'server_ip':m.group('ip'),
                         'uri':m.group('uri'),
                         'time':m.group('time'),
                         'status_code':m.group('status_code'),
                         'referral':m.group('referral'),
                         'agent':m.group('agent')})
        return True


    def determine_mimetype(self, line_data):
        """
        determine mimetype by comparing passed line_data with mimetype_matches
        """
        for mimetype_value,mimetype_match in self.mimetype_matches.items():
            if mimetype_match.match(line_data):
                return mimetype_value
        return "requests"


    def generate_mimetype_matches(self):
        """
        return dict of compiled regex matches and values for mimetypes
        """
        return {
                'image':re.compile(r'.*\.(?:png|jpg|jpeg|gif|tiff|svg|bmp|ico)'),
                'audio':re.compile(r'.*\.(?:mp3|aiff|m3u|wav|ram|mid|aif|snd)'),
                'application':re.compile(r'.*\.(?:pdf|xls|ogg)'),
                'video':re.compile(r'.*\.(?:mp2|mpa|mpe|mpeg|mpg|mpv2|mov|qt|avi|movie)'),
                'html':re.compile(r'.*\.(?:html|htm)'),
                'json':re.compile(r'.*\.(?:json)'),
                'javascript':re.compile(r'.*\.(?:javascript|js)'),
                'css':re.compile(r'.*\.(?:css)'),
                'xml':re.compile(r'.*\.(?:xml)')
              }



    def replay_requests(self, mimetype=''):
        """
        send requests to server
        """
        for data in self.log_data:
            if mimetype != '':
                if data['mimetype'] != mimetype:
                    continue
            request_str = ("http://%s%s"%(self.uri,
                                              data['uri']))
            try:
                print "sending request: %s"%(request_str)
                response = urllib2.urlopen((request_str))
            except Exception, e:
                print "Unable to complete the request: %s"%(request_str)
                print "Code: %s"%(e.code)
                print e.read()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', dest='filename_opt',
                       help="path to apache access log file",
                       required=True)
    parser.add_argument('-u', '--uri', dest='uri_opt',
                       help="base uri to send requests to", required=True)
    parser.add_argument('-m', '--mimetype', dest='mimetype_opt', default='',
                       help="send requests of mimetype")
    args = parser.parse_args()
    repache = Repache(args)
    repache.parse_log()
    repache.replay_requests(mimetype=args.mimetype_opt)
