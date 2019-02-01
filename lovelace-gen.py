import argparse
import os
import sys
import time

from ruamel.yaml import YAML
from ruamel.yaml.constructor import RoundTripConstructor
import jinja2

MAIN_FILE = 'main.yaml'
GENERATOR_MESSAGE = """
# This file is automatically generated by lovelace-gen.py
# https://github.com/thomasloven/homeassistant-lovelace-gen
# Any changes made to it will be overwritten the next time the script is run.
"""

def get_input_dir(inp):
    if not inp:
        if os.path.exists(os.path.join('/config/lovelace', MAIN_FILE)):
            return '/config/lovelace'
        if os.path.exists(os.path.join('lovelace/', MAIN_FILE)):
            return 'lovelace/'

    if os.path.exists(os.path.join(inp, MAIN_FILE)):
        return inp
    print("Input file main.yaml not found.", file=sys.stderr)
    sys.exit(2);

def process_file(path):
    global jinja
    template = jinja.get_template(path)
    yaml = YAML(typ='rt')
    yaml.preserve_quotes = True
    yaml.Constructor = RoundTripConstructor
    return yaml.load(template.render())

def include_statement(loader, node):
    return process_file(node.value)
RoundTripConstructor.add_constructor("!include", include_statement)

def file_statement(loader, node):
    path = node.value
    timestamp = time.time()
    if '?' in path:
        return f'{path}&{str(timestamp)}'
    else:
        return f'{path}?{str(timestamp)}'
RoundTripConstructor.add_constructor("!file", file_statement)

def main():
    global jinja
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input directory", nargs='?')
    parser.add_argument("-o", "--output", help="Output file")

    args = parser.parse_args()

    inp = get_input_dir(args.input)
    outp = args.output or os.path.join(inp, '..', 'ui-lovelace.yaml')

    jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(inp))

    try:
        data = process_file(MAIN_FILE)
    except Exception as e:
        print("Processing of yaml failed.")
        print(e)
        raise e
        sys.exit(3)

    try:
        with open(outp, 'w') as fp:
            fp.write(GENERATOR_MESSAGE)
            yaml = YAML()
            yaml.dump(data, fp)
    except Exception as e:
        print("Writing ui-lovelace.yaml failed.")
        print(e)
        sys.exit(4)

if __name__ == '__main__':
    main()
