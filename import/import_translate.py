#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#  Copyright (C) 2007 Jacek Śliwerski (rzyjontko)
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 2.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.  

from translate.storage import factory
from phrase import Phrase
from pysqlite2 import dbapi2 as sqlite

import dircache, sys


conn = sqlite.connect('../data/sixth.db')
cursor = conn.cursor()

cls = factory.getclass("kde.po")
langs = ['de', 'es', 'fr', 'it', 'ja', 'nl', 'pl', 'pt', 'pt_BR', 'ru', 'sv', 'tr']

def store_phrase(lid, sentence, lang):
    global cursor
    phrase = Phrase(sentence, lang)
    if phrase.length() == 0:
        return
    cursor.execute(u"insert into phrases(locationid, lang, phrase) values (?, ?, ?)", \
                   (lid, lang, sentence))
    cursor.execute(u"insert into canonical(locationid, lang, phrase) values (?, ?, ?)", \
                   (lid, lang, phrase.canonical ()))
    
def store_phrases(phrases):
    global cursor
    for source, ls in phrases.iteritems():
        cursor.execute(u"insert into locations (project) values (?)", ("KDE " + fname[:-3],))
        cursor.execute("select max (rowid) from locations")
        lid = cursor.fetchone()[0]
        store_phrase(lid, source, "C")
        for lang, target in ls.iteritems():
            store_phrase(lid, target, lang)

def load_file(phrases, fname, lang):
    global cls
    store = cls.parsefile('kde/' + lang + '/' + fname)
    for unit in store.units:
        l = phrases.setdefault(str(unit.source), {})
        l[lang] = str(unit.target)
    return len(store.units)

def store_file(fname):
    global langs
    phrases = {}
    for lang in langs:
        print "  + %s..." % lang,
        sys.stdout.flush()
        try:
            cnt = load_file(phrases, fname, lang)
            print "ok (%d)" % cnt
        except:
            print "failed."
        sys.stdout.flush()
    print "  phrases: %d" % len(phrases)
    store_phrases(phrases)

cursor.execute("drop index if exists loc_lang_idx")

for fname in dircache.listdir('kde/de'):
    print "Now importing %s..." % fname
    sys.stdout.flush()
    cursor = conn.cursor()
    store_file(fname)
    conn.commit()

cursor.execute("create index loc_lang_idx on phrases (locationid, lang)")
conn.close()
