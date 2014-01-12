#!/usr/bin/env python

import os
import sys
import shutil
from bs4 import BeautifulSoup


def parse_index(index_path):
    """Parses index.html file for chapters and sections."""

    index_file = open(index_path)
    soup = BeautifulSoup(index_file.read())
    scrape = {}
    chapters = [chap for chap in soup.ul.contents if chap != '\n']
    # chapters now contains a list of chapters (bs4 li elements)

    for chapter in chapters: # loop through chapters
        chapter_string = chapter.a.string
        if ':' in chapter_string:
            chapter_string = chapter_string[8:] # get ride of 'Chapter'
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

    os.mkdir(NEW_DIR)
    os.chdir(NEW_DIR)
    generate_course_index('.', NEW_DIR.replace('_', ' '), 'course')
    generate_chapters(index_scrape)

    os.chdir('..')


def generate_course_index(location, title, layout):
    """Generates the index.md for the entire course."""

    with open('%s/index.md' % location, 'w') as index:
        index.write('/*\n')
        # index.write('Title: ' + NEW_DIR.replace('_', ' ') + '\n')
        index.write('Title: %s\n' % title)
        index.write('layout: %s\n' % layout)
        index.write('*/\n')


def generate_chapters(index_scrape):
    """Generates directories and content for each course chapter."""

    for tuple in index_scrape:
        (chapter, chapter_file) = tuple
        if ':' in chapter: # if it's actual content
            chapter = chapter.replace(' ', '_')
            try: # get number of chapter from title
                chapter_num = int(chapter[:2])
                offset = 3
            except ValueError:
                chapter_num = chapter[:1]
                offset = 2
            chapter_name = chapter[offset:]
            chapter_dir = '%s.%s' % (chapter_num, chapter_name)
            os.mkdir(chapter_dir)
            generate_chapter_content(chapter_dir, index_scrape[tuple])
            generate_course_index(chapter_dir, chapter_name.replace('_', ' '), \
                                  'chapter')
        else: # non-content
            try:
                os.mkdir('Non-Content')
            except OSError:
                pass

            chapter = chapter.replace(' ', '_')
            chapter_md = '%s.md' % chapter
            non_content = generate_lesson_content(tuple)
            if non_content == None: # if there is nothing to write, write nothing
                continue
            with open('Non-Content/%s' % chapter_md, 'w') as non:
                non.write(non_content.encode('utf-8'))


def generate_chapter_content(chapter_dir, sections):
    """Populate with chapter directories with content."""

    for i, section in enumerate(sections, 1):
        section_file = '%d.%s.md' % (i, section[0].replace(' ', '_'))
        with open(chapter_dir + '/' + section_file, 'w') as lesson:
            lesson_content = generate_lesson_content(section)
            lesson.write(lesson_content.encode('utf-8'))


def generate_lesson_content(section):
    """Compile a string from origin lesson html to be written to new .md file"""

    with open('../%s/%s' % (DIR, section[1]), 'r') as lesson:
        soup = BeautifulSoup(lesson.read())
        # get learning objectives
        try:
            learning_obj = soup.find(class_='learning_objectives').text
        except AttributeError:
            learning_obj = '*None*'

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
            if element['class'] == [u'para', u'editable', u'block'] or \
               element['class'] == [u'title', u'editable', u'block']:
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
            return None

        # get key takeaways
        try:
            key_take = soup.find(class_='key_takeaways editable block').p.text
        except AttributeError:
            key_take = '*None*'

    lesson_full = """/*
Title: %s
layout: content
*/

# %s

## Learning Objectives

%s

## Content

%s

## Key Takeaways

%s
""" % (section[0], section[0], learning_obj, lesson_content, key_take)

    return lesson_full


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
