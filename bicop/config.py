# config.py
#
# Copyright 2002,2007 Wichert Akkerman <wichert@simplon.biz>
#
# This file is free software; you can redistribute it and/or modify it
# under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# Calculate shared library dependencies

"""Routines to read ISC config-alike configuration files.

There are a few changes from the real ISC Style:

 - comments start with a # and last until the end of the line
 - IP addresses are not supported, you will have to use strings for those

An example of a file in this format::

  # Example configuration
  
  datasource1 {
      server     "server1.your.domain";
      username   "client";
      password   "secret";
  };

  datasource2 {
      server     "server2.your.domain";
      username   "client";
      password   "secret";
  };

  tables {
      "users";
      "groups";
  }
"""

__docformat__	= "epytext en"

import shlex

class ParseError(Exception):
    """Parse error

    @ivar file:   file being parsed
    @type file:   string
    @ivar line:   linenumber
    @type line:   integer
    @ivar reason: problem description
    @type reason: string
    """
    def __init__(self, file, line, reason):
        self.file=file
        self.line=line
        self.reason=reason

    def __str__(self):
        return "%s[%d]: %s" % (self.file, self.line, self.reason)


def parse(input, filename=None, dictclass=dict):
    """Read a file in a ISC-like config style.

    The input can be either a file-like object or a string. If a string
    is used you can optionally also provide a filename, which will be
    used for raised exceptions.

    The contents from the file as returned as a standard python dictionary.
    """

    tokenizer=shlex.shlex(input, filename)
    tokenizer.wordchars+="/._"
    return _Parse(tokenizer, dictclass=dictclass)


def _Decode(token):
    if token[0]=='"':
        return token[1:-1]
    else:
        return int(token)


def _Parse(input, dictclass=dict):
    (type_list, type_dict)=(1, 2)
    stack=[]
    top=dictclass()

    type=type_dict

    try:
        command=input.get_token()
        while command:
            needsep=1
            if command=="}":
                (stack, top)=(stack[:-1], stack[-1])
                type=type_dict
            elif type==type_list:
                top.append(_Decode(command))
            else:
                value=input.get_token()
                if value=="{":
                    one=input.get_token();
                    two=input.get_token();
                    if two==";":
                        type=type_list;
                        top[command]=[]
                    else:
                        type=type_dict;
                        top[command]=dictclass()
                    input.push_token(two)
                    input.push_token(one)
                    stack.append(top)
                    top=top[command]
                    needsep=0
                elif value==";":
                    raise ParseError, (input.infile, input.lineno, 
                            "Unexpected separator found")
                else:
                    top[command]=_Decode(value)

            if needsep:
                separator=input.get_token()
                if separator!=";":
                    raise ParseError, (input.infile, input.lineno, 
                            "Required separator missing")

            command=input.get_token()
    except ValueError:
        raise ParseError, (input.infile, input.lineno, "Illegal value")
    except IndexError:
        raise ParseError, (input.infile, input.lineno, "Unexpected end of file")

    if stack:
        raise ParseError, (input.infile, input.lineno, "Unexpected end of file")
    
    return top

