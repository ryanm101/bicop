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
        self.file = file
        self.line = line
        self.reason = reason

    def __str__(self):
        return '{0}[{1}]: {2}'.format(self.file, str(self.line), self.reason)


def parse(_input, filename=None, dictclass=dict):
    """Read a file in a ISC-like config style.

    The input can be either a file-like object or a string. If a string
    is used you can optionally also provide a filename, which will be
    used for raised exceptions.

    The contents from the file as returned as a standard python dictionary.
    """

    tokenizer = shlex.shlex(_input, filename)
    tokenizer.wordchars += '/._'
    return _parse(tokenizer, dictclass=dictclass)


def _decode(token):
    if token[0] == '"':
        return token[1:-1]
    else:
        return int(token)


def _parse(_input, dictclass=dict):
    (type_list, type_dict) = (1, 2)
    stack = []
    top = dictclass()

    _type = type_dict

    try:
        command = _input.get_token()
        while command:
            needsep = 1
            if command == '}':
                (stack, top) = (stack[:-1], stack[-1])
                _type = type_dict
            elif _type == type_list:
                top.append(_decode(command))
            else:
                value = _input.get_token()
                if value == '{':
                    one = _input.get_token()
                    two = _input.get_token()
                    if two == ';':
                        _type = type_list
                        top[command] = []
                    else:
                        _type = type_dict
                        top[command] = dictclass()
                    _input.push_token(two)
                    _input.push_token(one)
                    stack.append(top)
                    top = top[command]
                    needsep = 0
                elif value == ';':
                    raise ParseError(_input.infile, _input.lineno, 'Unexpected separator found')
                else:
                    top[command] = _decode(value)

            if needsep:
                separator = _input.get_token()
                if separator != ';':
                    raise ParseError(_input.infile, _input.lineno, 'Required separator missing')

            command = _input.get_token()
    except ValueError:
        raise ParseError(_input.infile, _input.lineno, 'Illegal value')
    except IndexError:
        raise ParseError(_input.infile, _input.lineno, 'Unexpected end of file')

    if stack:
        raise ParseError(_input.infile, _input.lineno, 'Unexpected end of file')

    return top
