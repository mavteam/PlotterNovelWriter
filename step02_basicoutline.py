import re
import os
import json
import openai
from uuid import uuid4
from time import time,sleep
from random import seed,choice


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def save_json(filepath, payload):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        json.dump(payload, outfile, ensure_ascii=False, sort_keys=True, indent=1)


openai.api_key = open_file('openaiapikey.txt')


def gpt3_completion(prompt, engine='text-davinci-002', temp=1.1, top_p=1.0, tokens=3000, freq_pen=0.0, pres_pen=0.0, stop=['asdfasdf', 'asdasdf']):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()  # force it to fix any unicode errors
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            #text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            save_file('gpt3_logs/%s' % filename, prompt + '\n\n==========\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


def generate_section(file, variables):
    prompt = open_file(file)
    for i in list(variables.keys()):
        prompt = prompt.replace('<<%s>>' % i, variables[i])
    result = gpt3_completion(prompt)
    print('\n\n', result)
    return result


if __name__ == '__main__':
    unique_id = open_file('current_id.txt')
    synopsis = open_file('synopses/%s.txt' % unique_id)
    variables = {'SYNOPSIS': synopsis}
    print('\n\nSYNOPSIS:', synopsis)
    # theme
    theme = generate_section('prompt_theme.txt', variables)
    variables['THEME'] = theme
    # characters
    characters = generate_section('prompt_characters.txt', variables)
    variables['CHARACTERS'] = characters
    # setting
    setting = generate_section('prompt_setting.txt', variables)
    variables['SETTING'] = setting
    # plot
    plot = generate_section('prompt_plot.txt', variables)
    variables['PLOT'] = plot
    # save as JSON
    filepath = 'BasicOutlines/%s.json' % unique_id
    save_json(filepath, variables)