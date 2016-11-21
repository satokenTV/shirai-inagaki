# -*- coding: utf-8 -*-
import codecs
import re

import kanaconvert


class Morpheme:
    def __init__(self, surface, base, pos, adj):
        self.surface = surface
        self.base = base
        self.pos = pos
        self.adj = adj


class Phrase:
    def __init__(self, morphemes, modify_index, modified_indexes, voice, phrase_index):
        self.morphemes = morphemes
        self.modify_index = modify_index
        self.modified_indexes = modified_indexes
        self.voice = voice
        self.phrase_index = phrase_index

    def default(self):
        self.morphemes = []
        self.modify_index = -1
        self.modified_indexes = []
        self.voice = ""
        self.phrase_index = -1

    def have_pos(self, pos):
        for morpheme in self.morphemes:
            if pos == morpheme.pos:
                return True
        return False

    def get_have_pos_surface(self, pos):
        for morpheme in self.morphemes:
            if pos == morpheme.pos:
                return morpheme.surface
        return ""

    def get_have_pos_base(self, pos):
        for morpheme in self.morphemes:
            if pos == morpheme.pos:
                return morpheme.base
        return ''


class Sentence:
    def __init__(self, phrases):
        self.phrases = phrases

    def default(self):
        self.phrases = []

    def get_have_pos_phrases(self, pos):
        have_pos_phrases = []
        for phrase in self.phrases:
            if phrase.have_pos(pos):
                have_pos_phrases.append(phrase)
        return have_pos_phrases


def set_phrase_modified(sentence):
    for phrase in sentence.phrases:
        sentence.phrases[phrase.modify_index].modified_indexes.append(phrase.phrase_index)


def check_filtering_particle(particle):
    if particle != u'の' and particle != u'は':
        return False
    else:
        return True


def check_filtering_voice(voice):
    if voice != u"受動" and voice != u"使役":
        return False
    else:
        return True


def check_filtering_adj(phrase):
    takeirenyo_flag = False
    for morpheme in phrase.morphemes:
        if takeirenyo_flag:
            if morpheme.surface == "ある":
                return True
        takeirenyo_flag = False
        if morpheme.adj == u"タ系連用テ形":
            takeirenyo_flag = True
    return False


def decision_output(sentence):
    have_verb_phrases = sentence.get_have_pos_phrases(u"動詞")
    for have_verb_phrase in have_verb_phrases:
        if check_filtering_voice(have_verb_phrase.voice):
            continue
        if check_filtering_adj(have_verb_phrase):
            continue
        verb = have_verb_phrase.get_have_pos_base(u"動詞")
        result = verb
        for modified_index in have_verb_phrase.modified_indexes:
            if sentence.phrases[modified_index].have_pos(u"名詞") and sentence.phrases[modified_index].have_pos(u"助詞"):
                noun = sentence.phrases[modified_index].get_have_pos_surface(u"名詞")
                particle = sentence.phrases[modified_index].get_have_pos_surface(u"助詞")
                if check_filtering_particle(particle):
                    continue
                result = result + ' ' + noun + ' ' + kanaconvert.katakana(particle)
        if len(result.split(' ')) >= 3:
            print(result)


def init(sentence, phrase):
    sentence.default()
    phrase.default()


def main():
    input_file = codecs.open("doc0000000000.knp.txt", 'r', "utf-8")
    sentence = Sentence([])
    phrase = Phrase([], -1, [], '', -1)
    phrase_index = -1

    for line in input_file.readlines():
        if "EOS\n" == line:
            if phrase.morphemes:
                sentence.phrases.append(phrase)
            set_phrase_modified(sentence)
            decision_output(sentence)
            init(sentence, phrase)
            phrase_index = -1
            continue
        else:
            splited_line = line.split(" ")
            identifiers = [splited_line[0], splited_line[2][0]]
        if '*' == identifiers[0] and '<' == identifiers[1]:
            continue
        if '#' == identifiers[0] and 'U' == identifiers[1]:
            continue
        elif '+' == identifiers[0] and '<' == identifiers[1]:
            if phrase.morphemes:
                sentence.phrases.append(phrase)
            # ↑1句終わりとしての処理、↓1句はじめとしての処理
            modify_index = int(splited_line[1][:-1])
            voices = re.findall(r"<態:(.*?)>", line)
            if voices:
                voice = voices[0]
            else:
                voice = ''
            phrase_index += 1
            phrase = Phrase([], modify_index, [], voice, phrase_index)
        else:
            surface = splited_line[0]
            base = splited_line[2]
            pos = splited_line[3]
            adj = splited_line[9]
            phrase.morphemes.append(Morpheme(surface, base, pos, adj))

    input_file.close()

if __name__ == "__main__":
    main()
