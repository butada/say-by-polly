#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylint: disable=C0103

#from datetime import datetime
import os
import os.path
import hashlib
#import shutil
import sys
import subprocess
import re
import argparse
import inspect

#import logging.config
#import threading

#os.chdir(sys.path[0])
# logging.config.fileConfig("logging.conf")
# LOG = logging.getLogger()
#LOG.setLevel(logging.INFO)
g_args = None


def is_exists_cache(string):
    hash = get_hash(string)
    filename = './cache/{hash}.mp3'.format(**vars())
    ret = os.path.exists(filename)
    return ret


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if os.path.isdir(path):
            pass
        else:
            raise

def exec_cmd(command, silent=True):
    #LOG.debug('execCmd: "{command}"'.format(**vars()))

    proc = subprocess.Popen(
        command,
        shell  = True,
       # stdin  = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
    stdout_data, stderr_data = proc.communicate()
    #print(proc.returncode, stdout_data, stderr_data)
    #print(type(proc.returncode))
    #print(stdout_data)
    #print(stderr_data)
    #print(command)
    if silent == False and stderr_data != '':
        print('ERROR: ' + stderr_data.decode('utf-8'))

    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    caller = calframe[1][3]
    #stdout_data_strip = stdout_data.strip()
    #stderr_data_strip = stderr_data.strip()

    return stdout_data


def exec_mpg321(filename):
    return exec_cmd('sudo mpg321 {filename}'.format(**vars()))


def exec_polly(string_ssml, output_filename):
    #return util.execCmd('/usr/local/bin/aws polly synthesize-speech ' + \
    cmd = '/Users/butada/.pyenv/shims/aws polly synthesize-speech ' + \
                    ' --text-type ssml --output-format "mp3" ' + \
                    '--voice-id "Mizuki" ' + \
                    '--text "{string_ssml}" {output_filename}'.format(**vars())

    print('    execute:' + cmd)
    return exec_cmd(cmd)


def get_hash(string):
    ret_hash = hashlib.sha224(string.encode('utf-8')).hexdigest() # バイナリにエンコードしておかないとstrのままだとNGらしい
    return ret_hash


def say(string):
    hash = get_hash(string)
    output_filename = './cache/{hash}.mp3'.format(**vars())

    if is_exists_cache(string):
        pass
    else:
        prepare_cache(string)

    # DEBUG
    hash = get_hash(string)
    #LOG.debug('text="{string}" hash={hash}'.format(**vars()))
    print('    text="{string}" hash={hash}'.format(**vars()))

    #exec_mpg321(output_filename)


def transform_to_ssml(msg):
    msg = re.sub(r'洗面所', r"せんめん<prosody pitch='high'>じょ</prosody>", msg)
    msg = re.sub(r'公文', r"<sub alias='くもん'>公文</sub>", msg)
    msg = re.sub(r'神奈中', r"<sub alias='かなちゅう'>神奈中</sub>", msg)
    ret_msg = '<speak>{msg}</speak>'.format(**vars())
    return ret_msg


def prepare_cache(text):
    if is_exists_cache(text):
        pass
    else:
        mkdir_p('./cache')
        hash = get_hash(text)
        output_filename = './cache/{hash}.mp3'.format(**vars())
        print('    text:{text}, hash:{hash}'.format(**vars()))
        text_ssml = transform_to_ssml(text)
        # --text-type ssml付きに変更
        print('    text with ssml:' + text_ssml)
        exec_polly(text_ssml, output_filename)
        print('Generated new mp3 from AWS Polly.')


def check_args(args):
    args.pop(0) # remove program name on args[0]
    parser = argparse.ArgumentParser()
    parser.add_argument('input_text', metavar='message', type=str,
                        help='message')
    parser.add_argument('--create-cache-only', action='store_true')
    parser.add_argument('--english-mode', action='store_true')

    if args == []:
        ret_args = parser.parse_args([''])
    else:
        ret_args = parser.parse_args(args)

    return ret_args


def main(input_text, create_cache_only=False):
    messages = input_text
    messages = re.sub('(。|、|\n)+', '。\n', messages)
    messages = re.sub('\n$', '', messages)

    # Preparing
    print('Preparing polly cache...')
    for line in messages.split('\n'):
        prepare_cache(line)

    if create_cache_only:
        m = 'Finished due to create_cache_only option is specified.'
        print(m)
        #LOG.info(m)
        return

    # Saying
    print('Saying...')
    for line in messages.split('\n'):
        say(line)

    print('Finished.')


if __name__ == '__main__':
    args_orig = sys.argv
    g_args = check_args(args_orig)

    main(input_text=g_args.input_text,
         create_cache_only=g_args.create_cache_only,
         )


