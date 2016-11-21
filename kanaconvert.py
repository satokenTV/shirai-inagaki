import re


def hiragana(text):
    re_katakana = re.compile(r'[ァ-ン]')
    return re_katakana.sub(lambda x: chr(ord(x.group(0)) - 0x60), text)


def katakana(text):
    re_hiragana = re.compile(r'[ぁ-ん]')
    return re_hiragana.sub(lambda x: chr(ord(x.group(0)) + 0x60), text)
