#!/usr/bin/env python3
# coding=utf-8

import json
import os
import sys
import urllib.error
import urllib.request
import datetime
import configparser
import re
import subprocess

ai_name = ''
config_file = os.path.expanduser('~')+'/.config/vim-ai-token.json'
# change the path to your role file
role_file = os.path.expanduser(
    '~')+'/.vim/plugged/vim-ai-doubao/roles-example.ini'

is_debugging = False
debug_log_file = '/tmp/tgpt.log'

OPENAI_RESP_DATA_PREFIX = 'data: '
OPENAI_RESP_DONE = '[DONE]'


def replace_command_with_output(text):
    def replace(match):
        command = match.group(1)
        try:
            result = subprocess.check_output(
                command, shell=True, stderr=subprocess.STDOUT)
            return '\n'+result.decode('utf - 8').strip()+'\n'
        except subprocess.CalledProcessError as e:
            print(
                f"Command execution error: {e.output.decode('utf - 8').strip()}")
            sys.exit(-1)
    printDebug("Replace command with output: {}", text)
    return re.sub(r"`(.*?)`", replace, text)


def get_role_config(config_path):
    # read file from config
    config = configparser.ConfigParser()
    config.read(config_path)
    sections = config.sections()
    result = {}
    for section in sections:
        prompt = config[section]['prompt']
        result[section] = prompt
    printDebug("Role config: {}", result)
    return result


def normalize_config(config_path):
    # read file from config
    with open(config_path, 'r') as file:
        config_path = json.load(file)

    # if ai_name is empty, choose first key
    global ai_name
    if ai_name == '':
        ai_name = list(config_path.keys())[0]

    # normalize config
    normalized = {
        'engine': 'complete',
        'options': {
            'token': config_path[ai_name]['token'],
            'endpoint_url': config_path[ai_name]['endpoint_url'],
            'model': config_path[ai_name]['model'],
            'request_timeout': 60,
        },
    }
    return normalized


def make_openai_options(options):
    return {
        'model': options['model'],
    }


config = normalize_config(config_file)
engine = config['engine']

config_options = {
    **config['options'],
}
openai_options = make_openai_options(config_options)


def printDebug(text, *args):
    if not is_debugging:
        return
    with open(debug_log_file, "a") as file:
        file.write(f"[{datetime.datetime.now()}] " + text.format(*args) + "\n")


def openai_request(url, data, http_options, token):
    headers = {
        "Content-Type": "application/json",
    }
    headers['Authorization'] = f"Bearer {token}"

    request_timeout = http_options['request_timeout']
    req = urllib.request.Request(
        url,
        data=json.dumps({**data}).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=request_timeout) as response:
        for line_bytes in response:
            line = line_bytes.decode("utf-8", errors="replace")
            if line.startswith(OPENAI_RESP_DATA_PREFIX):
                line_data = line[len(OPENAI_RESP_DATA_PREFIX):-1]
                if line_data.strip() == OPENAI_RESP_DONE:
                    pass
                else:
                    openai_obj = json.loads(line_data)
                    yield openai_obj


def complete_engine(prompt):
    request = {
        'stream': True,
        'messages': [
            {
                'role': 'user',
                'content': prompt,
            }],
        **openai_options
    }
    http_options = {
        'request_timeout': config_options['request_timeout'],
    }
    printDebug("[engine-complete] request: {}", request)
    url = config_options['endpoint_url']
    response = openai_request(
        url, request, http_options, config_options['token'])

    def map_chunk(resp):
        printDebug("[engine-complete] response: {}", resp)
        return resp['choices'][0]['delta'].get('content', '')

    text_chunks = map(map_chunk, response)
    return text_chunks


def render_text_chunks(chunks):
    generating_text = False
    for text in chunks:
        if not text.strip() and not generating_text:
            continue  # trim newlines from the beginning
        generating_text = True
        print(text, end='', flush=True)

# get prompt for args[1...] to string


def get_prompt(args):
    if len(args) < 2:
        return ""
    if args[1] == "-h" or args[1] == "--help":
        print("Usage: tgpt.py /<role> <prompt>")
        sys.exit(0)
    if args[1].startswith("/"):
        role_aim = args[1][1:]
        config = get_role_config(role_file)
        if role_aim not in config:
            print(f"Role {role_aim} not found")
            sys.exit(-1)
        prompt = replace_command_with_output(config[role_aim])
        printDebug("Role prompt: {}", prompt)
        for arg in args[2:]:
            prompt += " " + arg
        return prompt
    else:
        prompt = ""
        for arg in args[1:]:
            prompt += replace_command_with_output(arg) + " "
        return prompt.strip()


prompt = get_prompt(sys.argv)
if prompt:
    chunks = complete_engine(prompt)
    render_text_chunks(chunks)
else:
    print("No prompt provided")
print("")
