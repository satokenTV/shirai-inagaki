# coding:utf-8
class Morpheme:
    def __init__(self, surface, base, pos, adj):
        self.surface = surface
        self.base = base
        self.pos = pos
        self.adj = adj

    def check_same_surface_base(self):
        if self.surface == self.base:
            return True
        else:
            return False

    def check_next_morpheme_pos(self, pos):
        if self.next_morpheme.pos == pos:
            return True
        else:
            return False
