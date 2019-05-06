#!/usr/bin/env python

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
    parser.add_argument('-e', '--extensions', help='file extensions to be considered as source files. separated with comma or a single "*" indicates all. e.g. "c,cpp,h,m,mm". default is "*"', default='*')
    parser.add_argument('-l', '--lines', help='limit the lines of source codes. but the content of a file is always complete, so the final lines may exceed this value. 0 for unlimited. default is 3500', type=int, default='3500')
    parser.add_argument('-o', '--output',  help='output file path. default is output.html', default='output.html')
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

    args.extension_patterns = _parse_extensions(args.extensions)

    if args.lines <= 0:
        args.lines = 2 ** 31

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

def _parse_extensions(extensions_string):
    if extensions_string.strip() == '*':
        return []
    array = extensions_string.split(',')
    array = ['*.' + e.strip() for e in array if len(e.strip()) > 0]
    array = list(set(array)) # remove duplicated values
    return array

def _short_class_name(obj):
    t = type(obj)
    m = re.match(r'<class \'(\w+\.)*(\w+)\'>', str(t))
    return m.group(2)

def _match_any_pattern(name, patterns):
    for pattern in patterns:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False

class Codes2HtmlTool:
    def __init__(self, args):
        self.args = args
        self.written_lines = 0
        with open(args.output, 'w') as write_fd:
            self.hf = HtmlFormatter()
            self.write_fd = write_fd
            write_fd.write(self._header())
            for path in args.sources:
                self._collect_files(path)
            write_fd.write(self._footer())

    def _should_ignore_file(self, name):
        return _match_any_pattern(name, self.args.ignore_patterns)
    
    def _accept_extension(self, name):
        patterns = self.args.extension_patterns
        return len(patterns) == 0 or _match_any_pattern(name, patterns)

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
            if self.written_lines >= self.args.lines:
                break
            if subfile.startswith('.'):
                continue
            full_path = os.path.join(path, subfile)
            if self._should_ignore_file(subfile):
                print('ignore "', full_path, '"', sep='')
                continue
            if os.path.isdir(full_path):
                self._collect_files(full_path)
            elif self._accept_extension(subfile):
                self._highlight_and_write_file(full_path)

    def _highlight_and_write_file(self, full_path):
        write_fd = self.write_fd
        hf = self.hf
        footer = self.args.file_footer
        try:
            lexer = get_lexer_for_filename(full_path)
            with open(full_path) as fd:
                lines = fd.readlines()
                self.written_lines += len(lines)
                content = ''.join(lines)
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