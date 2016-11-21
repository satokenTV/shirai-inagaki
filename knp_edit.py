# -*- coding: utf-8 -*-
import codecs


class Morpheme:
    def __init__(self, surface, base, pos):
        self.surface = surface
        self.base = base
        self.pos = pos


class Phrase:
    def __init__(self, morphemes, modify_index, modified_indexes, phrase_index):
        self.morphemes = morphemes
        self.modify_index = modify_index
        self.modified_indexes = modified_indexes
        self.phrase_index = phrase_index

    def default(self):
        self.morphemes = []
        self.modify_index = -1
        self.modified_indexes = []
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
        return ""


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


def decision_output(sentence):
    have_verb_phrases = sentence.get_have_pos_phrases(u"動詞")
    for have_verb_phrase in have_verb_phrases:
        verb = have_verb_phrase.get_have_pos_base(u"動詞")
        result = verb
        for modified_index in have_verb_phrase.modified_indexes:
            if sentence.phrases[modified_index].have_pos(u"名詞") and sentence.phrases[modified_index].have_pos(u"助詞"):
                noun = sentence.phrases[modified_index].get_have_pos_surface(u"名詞")
                particle = sentence.phrases[modified_index].get_have_pos_surface(u"助詞")
                if particle != u'の' and particle != u'は':
                    result = result + ' ' + noun + ' ' + particle
        if len(result.split(' ')) >= 3:
            print(result)


def init(sentence, phrase):
    sentence.default()
    phrase.default()


def main():
    input_file = codecs.open("doc0000000000.knp.txt", 'r', "utf-8")
    sentence = Sentence([])
    phrase = Phrase([], 0, [], 0)
    phrase_index = -1
# 全体的に変数名見直す
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
            line_split = line.split(" ")
            identifiers = []
            identifiers.append(line_split[0])
            identifiers.append(line_split[2][0])
        if '*' == identifiers[0] and '<' == identifiers[1]:
            continue
        if '#' == identifiers[0] and 'U' == identifiers[1]:
            continue
        elif '+' == identifiers[0] and '<' == identifiers[1]:
            if phrase.morphemes:
                sentence.phrases.append(phrase)
            # ↑1句終わりとしての処理、↓1句はじめとしての処理
            modify_index = int(line_split[1][:-1])
            phrase_index += 1
            phrase = Phrase([], modify_index, [], phrase_index)
        else:
            surface = line_split[0]
            base = line_split[2]
            pos = line_split[3]
            phrase.morphemes.append(Morpheme(surface, base, pos))

    input_file.close()

if __name__ == "__main__":
    main()
