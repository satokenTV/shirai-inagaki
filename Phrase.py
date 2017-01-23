# coding:utf-8
class Phrase:
    def __init__(self, morphemes, modify_index, modified_indexes, voice, form, phrase_index):
        self.morphemes = morphemes
        self.modify_index = modify_index
        self.modified_indexes = modified_indexes
        self.voice = voice
        self.form = form
        self.phrase_index = phrase_index

    def default(self):
        self.morphemes = []
        self.modify_index = -1
        self.modified_indexes = []
        self.voice = ''
        self.form = ''
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
