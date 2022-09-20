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


def gpt3_completion(prompt, engine='text-davinci-002', temp=0.7, top_p=1.0, tokens=2000, freq_pen=0.5, pres_pen=0.0, stop=['asdfasdf', 'asdasdf']):
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


def flesh_out_characters(story):
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
    return character_list


def flesh_out_theme(story):
    theme = story['THEME']
    print('Working on theme...')
    prompt = open_file('prompt_theme_light.txt').replace('<<THEME>>', theme)
    light = gpt3_completion(prompt, temp=1.0)
    prompt = open_file('prompt_theme_dark.txt').replace('<<THEME>>', theme)
    dark = gpt3_completion(prompt, temp=1.0)
    prompt = open_file('prompt_theme_understand.txt').replace('<<THEME>>', theme)
    understand = gpt3_completion(prompt, temp=1.0)
    result = '%s %s %s %s' % (theme, light, dark, understand)
    result = result.replace('\s+', ' ')
    print('THEME:', result)
    return result


def flesh_out_setting(story):
    print('Working on setting...')
    setting = story['SETTING']
    # TODO history, culture, religion, zeitgeist, mood, atmosphere, politics, economics, etc
    print('SETTING:', setting)
    return setting


def flesh_out_scenes(story):
    print('Working on scenes...')
    plot_elements = story['PLOT'].replace('\n\n','\n').splitlines()
    scenes = list()
    summary = 'Beginning of story.'
    count = 1
    idx = 1
    for plot in plot_elements:
        print('\n\n',count,'of',len(plot_elements))
        count = count + 1
        plot = re.sub('\d+:', '', plot).strip()  # clean up any numbered lists
        print('\n\nPLOT BEAT:', plot)
        prompt = open_file('prompt_plot_scene.txt').replace('<<SUMMARY>>', summary).replace('<<PLOT>>', plot)
        new_scenes = gpt3_completion(prompt, temp=0.5, engine='davinci', tokens=1000, stop=['STORY', 'Chapter', 'CHAPTER', '6'])
        new_scenes = new_scenes.replace('NEXT','').replace('SCENE','').replace(':','').strip()  # remove SCENE tags
        new_scenes = re.sub('\d+','', new_scenes)  # remove scene numbers
        new_scenes = re.sub('\n+','\n', new_scenes)  #  remove duplicate lines
        new_scenes = new_scenes.splitlines()  # split into list
        text = ''
        for i in new_scenes:
            i = i.strip()
            info = {'ID': idx, 'SCENE': i}  # it might be beneficial to have a "long version" and "short version" of each scene, for recursive summarization
            print(info)
            scenes.append(info)
            idx = idx + 1
            text = '%s %s' % (text, i)
        prompt = open_file('prompt_summary.txt').replace('<<STORY>>', '%s %s' % (summary, text))
        summary = gpt3_completion(prompt, temp=0.5).replace('\s+',' ')
        print('\n\nSUMMARY:', summary)
    pprint(scenes)
    return scenes


if __name__ == '__main__':
    unique_id = open_file('current_id.txt')
    story = open_json('BasicOutlines/%s.json' % unique_id)
    result = story
    # characters
    #character_list = flesh_out_characters(story)    
    #result['CHARACTERS'] = character_list
    # work on theme
    #theme = flesh_out_theme(story)
    #result['THEME'] = theme
    # work on setting
    # TODO GPT-3 is fucking awful at this
    #setting = flesh_out_setting(story)
    #result['SETTING'] = setting
    # work on plot
    scenes = flesh_out_scenes(story)
    result['SCENES'] = scenes
    # save as JSON
    filepath = 'AdvancedOutlines/%s.json' % unique_id
    save_json(filepath, result)
    print('\n\n=================================================\n\n')
    pprint(result)