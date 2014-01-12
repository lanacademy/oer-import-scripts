#!/usr/bin/env python

import os
import sys
import shutil
from bs4 import BeautifulSoup
import pdb


def parse_index(index_path):
    """Parses index.html file for chapters and sections."""

    index_file = open(index_path)
    soup = BeautifulSoup(index_file.read())
    scrape = {}
    chapters = [chap for chap in soup.ul.contents if chap != '\n']

    for chapter in chapters: # loop through chapters
        chapter_string = chapter.a.string
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

    pdb.set_trace()
    return scrape


def create_structure(dir, index_scrape):
    """
        Creates directory structure based off of data passed from the scraped
        index.html file.
    """

    new_dir = dir.replace('-', '_')
    os.mkdir(new_dir)
    generate_course_index(new_dir)
    generate_chapters(index_scrape)


def generate_course_index(course_name):
    """Generates the index.md for the entire course."""

    os.chdir(course_name)
    with open('index.md', 'w') as index:
        index.write('/*\n')
        index.write('Title: ' + course_name.replace('_', ' ') + '\n')
        index.write('layout: course\n')
        index.write('*/\n')
    os.chdir('..')


def generate_chapters(index_scrape):
    """Generates directories and content for each course chapter."""
    pass

def main():
    if len(sys.argv) != 2:
        print 'Usage: ./scraper.py [directory]'

    dir = sys.argv[1]
    index_scrape = parse_index(dir + '/index.html')
    create_structure(dir, index_scrape)


if __name__ == '__main__':
    main()
