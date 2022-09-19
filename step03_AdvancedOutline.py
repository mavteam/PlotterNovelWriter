import re
import os
import json
import openai
from uuid import uuid4
from pprint import pprint
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


def open_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return json.loads(infile.read())


openai.api_key = open_file('openaiapikey.txt')


def gpt3_completion(prompt, engine='text-davinci-002', temp=0.7, top_p=1.0, tokens=3000, freq_pen=0.0, pres_pen=0.0, stop=['asdfasdf', 'asdasdf']):
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
    story = open_json('BasicOutlines/%s.json' % unique_id)
    result = story
    #print(story['CHARACTERS'].replace('\n\n','\n'))
    # work on characters
    characters = story['CHARACTERS'].replace('\n\n','\n').splitlines()
    #print(characters)
    character_list = list()
    print('Working on characters...')
    for character in characters:
        # name
        prompt = open_file('prompt_character_name.txt').replace('<<CHARACTER>>', character)
        name = gpt3_completion(prompt, temp=0.0)
        # backstory
        prompt = open_file('prompt_character_backstory.txt').replace('<<SYNOPSIS>>', story['SYNOPSIS']).replace('<<CHARACTER>>', character)
        backstory = gpt3_completion(prompt).replace('\n\n','\n')
        # strengths and weaknesses
        prompt = open_file('prompt_character_strength_weakness.txt').replace('<<SYNOPSIS>>', story['SYNOPSIS']).replace('<<CHARACTER>>', character).replace('<<BACKSTORY>>', backstory)
        strengthweakness = gpt3_completion(prompt).replace('\n\n','\n')
        # beliefs and preferences
        prompt = open_file('prompt_character_belief_preference.txt').replace('<<SYNOPSIS>>', story['SYNOPSIS']).replace('<<CHARACTER>>', character).replace('<<BACKSTORY>>', backstory)
        beliefpreference = gpt3_completion(prompt).replace('\n\n','\n')
        # clean up
        prompt = open_file('prompt_character_cleanup.txt').replace('<<NAME>>', name).replace('<<BACKSTORY>>', backstory).replace('<<STRENGTHWEAKNESS>>', strengthweakness).replace('<<BELIEFPREFERENCE>>', beliefpreference)
        profile = gpt3_completion(prompt, temp=0.0)
        # all done
        info = {'NAME': name, 'PROFILE': profile}
        character_list.append(info)
    pprint(character_list)
    result['CHARACTERS'] = character_list
    # work on plot
    # work on setting
    # work on theme