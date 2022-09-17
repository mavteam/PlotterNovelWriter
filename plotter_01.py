import re
import os
import openai
from time import time,sleep
from random import seed,choice
from uuid import uuid4


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


openai.api_key = open_file('openaiapikey.txt')


def gpt3_completion(prompt, engine='text-davinci-002', temp=0.7, top_p=1.0, tokens=1000, freq_pen=0.0, pres_pen=0.0, stop=['asdfasdf', 'asdasdf']):
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


if __name__ == '__main__':
    # pick a random premise
    seed()
    file = choice(os.listdir('premises/'))
    premise = open_file('premises/%s' % file)
    print('\n\nPREMISE:',premise)
    # generate a title for the story
    prompt = open_file('prompt_title.txt').replace('<<UUID>>', str(uuid4())).replace('<<PREMISE>>', premise)
    title = gpt3_completion(prompt, temp=1.0).replace('"','').replace("'",'')
    story_path = 'stories/%s/' % title.replace('The ', '').replace(' ','').replace(':','')
    os.mkdir(story_path)
    save_file(story_path + 'title.txt', title)
    print('\n\nTITLE:', title)
    # generate a theme
    prompt = open_file('prompt_theme.txt').replace('<<UUID>>', str(uuid4())).replace('<<PREMISE>>', premise).replace('<<TITLE>>', title)
    theme = gpt3_completion(prompt, temp=1.0).replace('"','').replace("'",'')
    save_file(story_path + 'theme.txt', theme)
    print('\n\nTHEME:', theme)
    # generate a setting
    prompt = open_file('prompt_setting.txt').replace('<<UUID>>', str(uuid4())).replace('<<PREMISE>>', premise).replace('<<TITLE>>', title).replace('<<THEME>>', theme)
    setting = gpt3_completion(prompt, temp=1.0).replace('"','').replace("'",'')
    save_file(story_path + 'setting.txt', setting)
    print('\n\nSETTING:', setting)
    # generate some characters
    prompt = open_file('prompt_characters.txt').replace('<<UUID>>', str(uuid4())).replace('<<PREMISE>>', premise).replace('<<TITLE>>', title).replace('<<THEME>>', theme).replace('<<SETTING>>', setting)
    characters = gpt3_completion(prompt, temp=1.0).replace('"','').replace("'",'')
    save_file(story_path + 'characters.txt', characters)
    print('\n\nCHARACTERS:', characters)
    # generate some plot!
    prompt = open_file('prompt_outline.txt').replace('<<UUID>>', str(uuid4())).replace('<<PREMISE>>', premise).replace('<<TITLE>>', title).replace('<<THEME>>', theme).replace('<<SETTING>>', setting).replace('<<CHARACTERS>>', characters)
    outline = gpt3_completion(prompt, temp=1.0).replace('"','').replace("'",'')
    save_file(story_path + 'outline.txt', outline)
    print('\n\nOUTLINE:', outline)
