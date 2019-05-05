import os
import sys
import re
import fnmatch
import argparse
import time
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename
from pygments.formatters.html import DOC_HEADER
from pygments.formatters.html import DOC_FOOTER

def _parse_args():
    parser = argparse.ArgumentParser(description='A tool to collect codes and highlight syntax in a single html document.')
    parser.add_argument('sources', metavar='source', nargs='+', type=str, help='source code directory or file')
    parser.add_argument('-o', '--out',  help='output file path. default is output.html', default='output.html', dest='output')
    parser.add_argument('-i', '--ignore', help='path of the ignore file, similar to .gitignore. default is ignore.txt', default='ignore.txt', dest='ignore_file')
    parser.add_argument('-f', '--footer', help='file footer string, you can use </br> to insert lines. default is </br>', default='</br>', dest='file_footer')
    args = parser.parse_args()

    sources = []
    for s in args.sources:
        s = os.path.expanduser(s).rstrip(os.path.sep)
        if os.path.exists(s):
            sources.append(s)
        else:
            print('error: "', s, '" does not exists!', sep='')
    if len(sources) != len(args.sources):
        return None
    args.sources = sources
    
    args.output = os.path.expanduser(args.output)

    args.ignore_file = os.path.expanduser(args.ignore_file)
    args.ignore_patterns = _parse_ignore_file(args.ignore_file)

    return args

def _parse_ignore_file(path):
    if not os.path.exists(path):
        print('warning: no ignore file specified, all codes will be collected')
        return []
    try:
        with open(path, 'r') as fd:
            ss = fd.readlines()
            ss = [s.strip('\n') for s in ss if len(s.strip('\n')) > 0]
            return ss
    except:
        return []

def _short_class_name(obj):
    t = type(obj)
    m = re.match(r'<class \'(\w+\.)*(\w+)\'>', str(t))
    return m.group(2)

class Codes2HtmlTool:
    def __init__(self, args):
        self.args = args
        with open(args.output, 'w') as write_fd:
            self.hf = HtmlFormatter()
            self.write_fd = write_fd
            write_fd.write(self._header())
            for path in args.sources:
                self._collect_files(path)
            write_fd.write(self._footer())

    def _should_ignore_file(self, name):
        for pattern in self.args.ignore_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False
    
    def _header(self):
        return DOC_HEADER % dict(
            title = self.hf.title, 
            styledefs = self.hf.get_style_defs('body'), 
            encoding = self.hf.encoding)

    def _footer(self):
        return DOC_FOOTER

    def _collect_files(self, path):
        subfiles = os.listdir(path)
        subfiles.sort()
        for subfile in subfiles:
            if subfile.startswith('.'):
                continue
            full_path = os.path.join(path, subfile)
            if self._should_ignore_file(subfile):
                print('ignore "', full_path, '"', sep='')
                continue
            if os.path.isdir(full_path):
                self._collect_files(full_path)
            else:
                self._highlight_and_write_file(full_path)

    def _highlight_and_write_file(self, full_path):
        write_fd = self.write_fd
        hf = self.hf
        footer = self.args.file_footer
        try:
            lexer = get_lexer_for_filename(full_path)
            with open(full_path) as fd:
                content = fd.read()
                if full_path.endswith('.h'):
                    # ".h" file is possible to be objective-c.
                    # guess again with file content to determine the actual syntax
                    lexer = get_lexer_for_filename(full_path, code=content)
                formatted = highlight(content, lexer, hf)
                write_fd.write(formatted)
                write_fd.write(footer)
                print('highlighted with ', _short_class_name(lexer), ': "', full_path, '"', sep='')
        except:
            print('not source code: "', full_path, '"', sep='')

if __name__ == "__main__":
    t1 = time.time()
    args = _parse_args()
    if args is not None:
        Codes2HtmlTool(args)
    t2 = time.time()
    print('total time: %.1fs' % (t2 - t1))