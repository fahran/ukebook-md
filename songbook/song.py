#!/usr/bin/env python3
# vim: set ts=4 sts=4 sw=4 et ci nu ft=python:

import os

# object-oriented wrapper around song objects
import codecs
import markdown
import ukedown.udn

from bs4 import BeautifulSoup as bs

class Song(object):
    """
    a Song object represents a song with associated methods
    to generate output, summarise content etc
    songs are instantiated from ukedown files

    This wrapper is intended to make it simpler to construct a DB model
    for this content
    """

    def __init__(self, src, **kwargs):
        """
        construct our song object from a ukedown (markdown++) file
        Args:
            markup(str):     ukedown content read from a file. This must be unicode (UTF-8)

            fh(file handle): an open file handle (or equivalent object)
                             supporting 'read' (stringIO etc). This should
                             produce UTF-8 when read (codecs.open is your friend)
            src(path):       path to a ukedown-formatted file to open and parse

        Kwargs:
            anything can be customised, most attributes/properties are
            auto-generated, but we sometimes need to override them
            The following are common properties - '*' indicates optional

            title(str):      Song Title
            title_sort(str): Song title in sortable order
            artist(str):     artist name, as printed
            artist_sort:     sortable artist name, usually either "Surname, Firstname"
                             or "Band Name, The" where appropriate.
            tags(list):      tags to apply to this song (tentative, tested etc)

        """

        if os.path.exists(src):
            self.__load(src)
            self._filename = src
        else:
            # presume we've been given content
            self._markup = src


        # does nothing yet
        self._filename = src
        self.__parse(markup=self._markup)

        self._tags = set([])


        # update with any parameters...
        for key, val in  kwargs.items():
            setattr(self, key, val)

        if self._filename is None:
            self._filename = ('{0.title}_-_{0.artist}'.format(self)).lower()

    def __load(self, sourcefile):
        """
        utlity function to handle loading from a file-like object
        """
        try:
            with codecs.open(sourcefile, mode='r', encoding='utf-8') as src:
                self._markup = src.read()
        except (IOError, OSError) as E:
            print("Unable to open input file {0.filename} ({0.strerror}".format(E))
            self._markup = None


    def __parse(self, markup=None):
        """
        parses ukedown to set attrs and properties
        """
        if markup is None:
            markup = self._markup
        raw_html = markdown.markdown(markup,
                                     extensions=[
                                       'markdown.extensions.nl2br',
                                       'ukedown.udn']
                                    )
        # process HTML with BeautifulSoup to parse out headers etx
        soup = bs(raw_html, features='lxml')

        # extract our sole H1 tag, which should be the title - artist string
        hdr = soup.h1.extract()
        try:
            title, artist = [ i.strip() for i in hdr.text.split('-', 1) ]
        except ValueError:
            title = hdr.text.strip()
            artist = None
        # remove the header from our document
        hdr.decompose()

        # now parse out all chords used in this songsheet
        # ideally keep ordering, so can't use python sets
        chordlist = []
        for crd in soup.findAll('span', {'class': 'chord'}):
            cname = crd.text.split().pop(0)
            if cname not in chordlist:
                chordlist.append(cname)

        # set attributes for this song
        self._chords = chordlist
        self._title = title
        self._artist = artist

        # add processed body text (with headers etc converted)
        self.body = ''.join([ str(x) for x in soup.body.contents ])

    def render(self, template):
        """
        Render HTML output
        """
        pass

    def pdf(self):
        """
        Generate a PDF songsheet from this song
        """
        pass

    @property
    def markup(self):
        return self._markup

    @markup.setter
    def markup(self, content):
        self._markup = content

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, path):
        self._filename = path

    @property
    def artist(self):
        return self._artist

    @artist.setter
    def artist(self, value):
        self._artist = artist

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    # no setter for chords, they're parsed from input
    @property
    def chords(self):
        return self._chords

    # tags are read-only too (ish)
    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, taglist):
        self._tags = set(taglist)

    def tag(self, tag):
        if tag not in self.tags:
            self._tags.add(tag)

    def untag(self, tag):
        if tag in self._tags:
            self._tags.pop(tag)

    def clear_tags(self):
        # remoes ALL tags
        self._tags = set([])



