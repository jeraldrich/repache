import re

matches = {
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
