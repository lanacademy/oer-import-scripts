#!/usr/bin/env python

import os
import sys
import shutil
import re
from bs4 import BeautifulSoup


def file_write(file_obj, text):
    """Utility function to ensure writing with ascii."""
    
    file_obj.write(text.encode('utf-8'))

def parse_index(index_path):
    """Parses index.html file for chapters and sections."""

    soup = BeautifulSoup(open(index_path))
    scrape = {}
    chapters = [chap for chap in soup.ul.contents if chap != '\n']
    # chapters now contains a list of chapters (bs4 li elements)

    for chapter in chapters: # loop through chapters
        chapter_string = chapter.a.string
        if 'Chapter' in chapter_string:
            chapter_string = chapter_string.replace('Chapter ', '') # get ride of 'Chapter'
            chapter_string = chapter_string.replace(' ', '', 1) # delete space after colon
        chapter_file = chapter.a['href']
        chapter_tuple = (chapter_string, chapter_file)
        scrape[chapter_tuple] = []
        if chapter.li != None: # filter out non-content chapters
                               # (Preface, Acknowledgements, etc)
            for section in chapter.find_all('li'):
                section_string = section.a.string
                section_file = section.a['href']
                section_tuple = (section_string, section_file)
                scrape[chapter_tuple].append(section_tuple)

    return scrape


def create_structure(index_scrape):
    """
        Creates directory structure based off of data passed from the scraped
        index.html file.
    """

    global keywords # if you can think of a better way, let me know :/
    keywords = {}
    os.mkdir(NEW_DIR)
    os.chdir(NEW_DIR)
    generate_template('.', 'index.md', NEW_DIR.replace('_', ' '), 'course')
    generate_chapters(index_scrape)
    generate_keywords()
    os.chdir('..')


def generate_template(location, filename, title, layout):
    """Generates general template with header."""

    with open('%s/%s' % (location, filename), 'w') as index:
        index.write('/*\n')
        file_write(index, 'Title: %s\n' % title)
        file_write(index, 'layout: %s\n' % layout)
        index.write('*/\n\n')

        if layout == 'chapter':
            index.write('## Chapter Learning Objectives\n\n')
        elif layout == 'review':
            index.write('## Key Takeaways\n\n')


def generate_chapters(index_scrape):
    """Generates directories and content for each course chapter."""

    for tuple in index_scrape: # for each chapter
        (chapter, chapter_file) = tuple
        # if ':' in chapter: # if it's actual content
        if re.search('^[0-9]+:', chapter): # if it's actual content (has #:)
            chapter = chapter.replace(' ', '_')
            try: # get number of chapter from title
                chapter_num = int(chapter[:2])
                offset = 3
            except ValueError:
                chapter_num = int(chapter[:1])
                offset = 2
            chapter_name = chapter[offset:]
            chapter_dir = '%d.%s' % (chapter_num, chapter_name)
            os.mkdir(chapter_dir)
            generate_template(chapter_dir, 'index.md', \
                              chapter_name.replace('_', ' '), \
                              'chapter')
            generate_template(chapter_dir, '%s_review.md' % chapter_dir,
                              chapter_name.replace('_', ' '), 'review')
            generate_chapter_content(chapter_dir, index_scrape[tuple])
        else: # non-content
            try:
                os.mkdir('Non-Content')
            except OSError:
                pass

            chapter = chapter.replace(' ', '_')
            chapter_md = '%s.md' % chapter
            non_content = parse_section(tuple)
            if non_content == None: # if there is nothing to write, write nothing
                continue
            with open('Non-Content/%s' % chapter_md, 'w') as non:
                file_write(non, non_content[0])


def generate_chapter_content(chapter_dir, sections):
    """Populate chapter directories with content."""

    for i, section in enumerate(sections, 1):
        section_file = '%d.%s' % (i, section[0].replace(' ', '_'))
        lesson_content, learning_obj, key_take, exercises = parse_section(section)
        with open('%s/%s.md' % (chapter_dir, section_file), 'w') as lesson:
            file_write(lesson, lesson_content)
        with open('%s/index.md' % chapter_dir, 'a') as index:
            if 'None' not in learning_obj:
                file_write(index, '### Section %d - %s\n\n' % (i, section[0]))
                file_write(index, learning_obj)
        with open('%s/%s_review.md' % (chapter_dir, chapter_dir), 'a') as rev:
            if 'None' not in key_take:
                file_write(rev, '### Section %d - %s\n\n' % (i, section[0]))
                file_write(rev, key_take)
                rev.write('\n\n')
        if 'None' not in exercises:
            generate_template(chapter_dir, '%s_questions.md' % section_file, \
                              section[0], 'questions')
            with open('%s/%s_questions.md' % (chapter_dir, section_file), 'a') as ques:
                file_write(ques, exercises)


def parse_section(section):
    """
        Parse relevant information out of the original section html file,
        such as learning objectives, actual educational content,
        key takeaways, exercises, and keywords.
    """

    with open('../%s/%s' % (DIR, section[1]), 'r') as lesson:
        soup = BeautifulSoup(lesson.read())
        # get learning objectives
        learning_obj = []
        
        try:
            learning_obj.append(soup.find(class_='learning_objectives').p.text)
        except AttributeError:
            pass
        
        try:
            learning_obj.append(soup.find(class_='learning_objectives').ol.text)
        except AttributeError:
            pass

        learning_obj.append('\n\n')

        if learning_obj == ['\n\n']:
            learning_obj = '*None*'
        else:
            learning_obj = ''.join(learning_obj)

        # get keywords
        # uses the ever unfortunate 'keywords' global variable
        try:
            words = soup.find_all(class_='margin_term')
            for word in words:
                term = word.a.text
                definition = word.span.text
                keywords[term] = definition
        except AttributeError:
            pass

        # get lesson content
        # I need to get every tag whose class is either "title editable block"
        # or "para editable block"
        lesson_content = []
        content_scrape = soup.find_all(class_='editable') # gets us close
        del content_scrape[0]
        content_scrape_2 = []
        for element in content_scrape: # this is a really bad way of doing
                                       # this but I can't figure out another
                                       # way right now :(
            if element['class'][0] == u'para' or \
               element['class'][0] == u'title' or \
               element['class'][0] == u'itemizedlist':
                content_scrape_2.append(element) # finishes off the job

        for element in content_scrape_2: # assemble the list
            try:
                element.find(class_='glossdef').decompose() # remove special definition tag
                                                            # for vocab words
            except AttributeError:
                pass
            if 'title' in element['class']:
                lesson_content.append('### ')
            lesson_content.append(element.text)
            lesson_content.append('\n\n')
        lesson_content = ''.join(lesson_content)
        if lesson_content == '':
            lesson_content = '*None*'

        # get key takeaways...i'm so sorry
        try:
            key_take = soup.find(class_='key_takeaways editable block').p.text
            # key_take = soup.find(class_='key_takeaways editable block').text
        except AttributeError:
            try:
                key_take = soup.find(class_='key_takeaways editable block').ul.text
            except AttributeError:
                try:
                    key_take = soup.find(class_='key_takeaways editable block').text
                except AttributeError:
                    key_take = '*None*'

        # get exercises
        try:
            exercises = soup.find(class_='exercises editable block')
            exercises_str = ['### Exercises\n']
            exercises_li = exercises.find_all('li')
            if exercises_li == []:
                exercises_str.append('- ' + exercises.find('p').text)
            else:
                for ex in exercises_li:
                    exercises_str.append('- ' + ex.text)
        except AttributeError: 
            exercises = '*None*'

        if exercises != '*None*':
            exercises = '\n'.join(exercises_str)

        # put it all together
    lesson_full = """/*
Title: %s
layout: article
*/

# %s

## Learning Objectives

%s

---

## Content

%s

---

## Key Takeaways

%s
""" % (section[0], section[0], learning_obj, lesson_content, key_take)

    return lesson_full, learning_obj, key_take, exercises


def generate_keywords():
    """
        Generates keywords.xml files based off of global 'keywords'
        dictionary containing term/definition pairs.
    """

    with open('keywords.xml', 'w') as keyw:
        keyw.write('<data>\n')
        for term in sorted(keywords.keys()):
            file_write(keyw, '<title>%s</title>' % term)
            file_write(keyw, '<text>%s</text>\n' % keywords[term])
        keyw.write('</data>')

def main():
    if len(sys.argv) != 2:
        print 'Usage: ./scraper.py [directory]'
        sys.exit()

    global DIR, NEW_DIR
    DIR = sys.argv[1]
    NEW_DIR = DIR.replace('-', '_')

    index_scrape = parse_index(DIR + '/index.html')
    create_structure(index_scrape)


if __name__ == '__main__':
    main()
