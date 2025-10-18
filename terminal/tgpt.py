#!/usr/bin/env python3
# coding=utf-8

import json
import os
import sys
import urllib.request
import datetime
import configparser
import re
import platform
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


def excape_md_format(text):
    replace_arr = ["```bash", "```json", "```", "\n"]
    for i in replace_arr:
        text = text.replace(i, "")
    return text


def set_clipboard_text(text):
    system = platform.system()
    if system == "Windows":
        # Windows 系统使用 clip 命令（但 clip 命令需要在 cmd 中运行，这里通过 PowerShell 来调用）
        command = ['powershell', 'Set-Clipboard', '-Value', text]
    elif system == "Linux":
        # Linux 系统使用 xclip 命令
        command = ['xclip', '-selection', 'clipboard']
    elif system == "Darwin":  # macOS 系统
        # macOS 系统使用 pbcopy 命令
        command = ['pbcopy']
    else:
        raise OSError(f"不支持的操作系统: {system}")

    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'), timeout=3)
    except subprocess.CalledProcessError as e:
        print(f"执行命令时出错: {e}")
        exit(-1)
    except FileNotFoundError:
        print(f"未找到对应的剪贴板操作命令，可能是系统未安装相应工具。")
        exit(-1)


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
    printDebug("Role config: {}", config)
    return config


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


def complete_engine(prompt, before_messages=None):
    messages = []

    if before_messages:
        for i, message in enumerate(before_messages):
            if i % 2 == 0:
                messages.append({
                    'role': 'user',
                    'content': message,
                })
            else:
                messages.append({
                    'role': 'assistant',
                    'content': message,
                })

    messages.append({
        'role': 'user',
        'content': prompt,
    })

    request = {
        'stream': True,
        'messages': messages,
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
    full_text = ""
    for text in chunks:
        if not text.strip() and not generating_text:
            continue  # trim newlines from the beginning
        generating_text = True
        full_text += text
        print(text, end='', flush=True)
    return full_text


def get_prompt(args):
    # get prompt for args[1...] to string
    extra_config = {}
    if len(args) < 2:
        return "", extra_config
    pos = 1

    if args[pos] == "-h" or args[pos] == "--help":
        print("Usage: tgpt.py --chat/-c(optional) /<role>(optional) <prompt>")
        sys.exit(0)

    # use as chat
    if args[pos] == "-c" or args[pos] == "--chat":
        extra_config['chat'] = True
        pos += 1

    if len(args) > pos and args[pos].startswith("/"):
        role_aim = args[pos][1:]
        config = get_role_config(role_file)
        if role_aim not in config:
            print(f"Role {role_aim} not found")
            sys.exit(-1)

        if 'prompt' not in config[role_aim]:
            print(f"Role {role_aim} has no prompt")
            sys.exit(-1)
        if 'copy' in config[role_aim]:
            # make it into bool type
            if config[role_aim]['copy'] == 'true':
                extra_config['copy'] = True
            else:
                extra_config['copy'] = False
        if 'chat' in config[role_aim]:
            # make it into bool type
            if config[role_aim]['chat'] == 'true':
                extra_config['chat'] = True
            else:
                extra_config['chat'] = False

        prompt = replace_command_with_output(config[role_aim]['prompt'])
        printDebug("Role prompt: {}", prompt)
        for arg in args[pos+1:]:
            prompt += " " + arg
        return prompt, extra_config
    else:
        prompt = ""
        for arg in args[pos:]:
            prompt += replace_command_with_output(arg) + " "
        return prompt.strip(), extra_config


prompt, extra_config = get_prompt(sys.argv)
is_copy = 'copy' in extra_config and extra_config['copy']
is_chat = 'chat' in extra_config and extra_config['chat']
only_code = 'only_code' in extra_config and extra_config['only_code']

if prompt:
    chunks = complete_engine(prompt)
    full_text = render_text_chunks(chunks)
    if is_copy and sys.stdout.isatty():
        set_clipboard_text(excape_md_format(full_text))
        print(" (Result has copied to clipboard)")

    messages = [prompt]
    messages.append(full_text)
    while is_chat:
        print("\n")
        print("> ", end="")
        sys.stdout.flush()
        user_input = input()
        if user_input.strip() == "exit" or user_input.strip() == "quit" or user_input.strip() == "q":
            break

        prompt = user_input
        chunks = complete_engine(prompt, messages)
        full_text = render_text_chunks(chunks)

        messages.append(user_input)
        messages.append(full_text)
        if full_text.strip() == "":
            break
else:
    print("No prompt provided")
print("")
