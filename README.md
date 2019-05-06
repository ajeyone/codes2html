# codes2html
A tool to collect codes into a HTML document with syntax highlighted, written in python (tested with python 3.7 on Mac computer).

The original intention of this tool is for the source code part of ["软件著作权"](https://baike.baidu.com/item/%E8%BD%AF%E4%BB%B6%E8%91%97%E4%BD%9C%E6%9D%83), but you may find other usages of collecting codes to a single file.

The script uses [pygments](http://pygments.org/) to highlight codes.

The script walks through the source paths, and collect all source codes that pygments supports.

If any bug or problem please report an issue.

## pygments
Install:
```
pip install Pygments
```
In the script, "guess" feature is used to determine the source code syntax, both file name and file content are considered.

## Usage
```
usage: codes2html.py [-h] [-e EXTENSIONS] [-l LINES] [-o OUTPUT]
                     [-i IGNORE_FILE] [-f FILE_FOOTER]
                     source [source ...]

A tool to collect codes and highlight syntax in a single html document.

positional arguments:
  source                source code directory or file

optional arguments:
  -h, --help            show this help message and exit
  -e EXTENSIONS, --extensions EXTENSIONS
                        file extensions to be considered as source files.
                        separated with comma or a single "*" indicates all.
                        e.g. "c,cpp,h,m,mm". default is "*"
  -l LINES, --lines LINES
                        limit the lines of source codes. but the content of a
                        file is always complete, so the final lines may exceed
                        this value. 0 for unlimited. default is 3500
  -o OUTPUT, --output OUTPUT
                        output file path. default is output.html
  -i IGNORE_FILE, --ignore IGNORE_FILE
                        path of the ignore file, similar to .gitignore.
                        default is ignore.txt
  -f FILE_FOOTER, --footer FILE_FOOTER
                        file footer string, you can use </br> to insert lines.
                        default is </br>
```