import json
import re
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pydub import AudioSegment
from furigana.furigana import split_furigana


DATA_ROOT = Path('./data/')


def decrypt(filename, key):
    # dat file -> json
    iv = bytearray(16)
    with open(filename, 'rb') as f:
        data = f.read()
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    data = unpad(cipher.decrypt(data), AES.block_size)
    return json.loads(data.decode('utf-8'))


def get_ms(t):
    sec = 0
    for x in t.split(':'):
        sec = sec * 60 + float(x)
    return sec * 1000


def export_audo_clip(file_in, file_out, start, end):
    audio = AudioSegment.from_mp3(file_in)
    clip = audio[get_ms(start)+1000:get_ms(end)]
    clip.export(file_out)


def to_furigana(text):
    try:
        s = []
        for pair in split_furigana(text):
            if len(pair) == 2:
                kanji, hira = pair
                s.append(" %s[%s] " % (kanji, hira))
            else:
                s.append(pair[0])
        return ''.join(s)
    except IndexError:
        print(text)
        return text


def to_txt(sent_list, filename):
    lines = []
    for idx, e in enumerate(sent_list):
        lines.append('\t'.join([
            f'{idx+1:04d}',
            e['jp'],
            e['cn'],
            e['audio'],
            str(e['lesson']),
            e['section'],
            e['tags'],
        ])+'\n')
    with open(filename, 'w') as f:
        f.writelines(lines)


def process_basic(book, unit, lesson, key):
    lesson_path = \
            DATA_ROOT / f'book{book}/book{book}-unit{unit}/lesson{lesson}'
    basic_dat_fn = lesson_path / 'basic.dat'
    audio_fn = lesson_path / 'lesson_basic.pepm'

    d = decrypt(basic_dat_fn, key)
    res = []

    sec = None
    txt_buff_cn = []
    txt_buff_jp = []
    start, end = 0, 0
    for c in (d['content'] + [{'content': '#'}]):
        if c['content'] != '#' and not c['trans']:
            continue
        txt_jp = re.sub(r'<[^>]*>', '', c['content'])
        if txt_jp[0] in 'ＡＢＣＤ':
            txt_jp = 'ABCD'['ＡＢＣＤ'.find(txt_jp[0])] + txt_jp[1:]
        if txt_jp[0] in '1234ABCD#':
            if sec:
                clip_fn = f'book{book}-lesson{lesson:02d}-basic-{sec}.mp3'
                res.append({
                    'jp': '<br>'.join(txt_buff_jp),
                    'cn': '<br>'.join(txt_buff_cn),
                    'audio': f'[sound:{clip_fn}]',
                    'lesson': lesson,
                    'section': sec,
                    'tags': f'book{book} book{book}-lesson{lesson:02d}'
                })
                export_audo_clip(
                        audio_fn, f'./output/audio/{clip_fn}', start, end)

                txt_buff_cn.clear()
                txt_buff_jp.clear()
            if txt_jp == '#':
                continue
            sec = txt_jp[0]
            start = c['starttime']
            txt_jp = txt_jp[1:].lstrip('.').strip()

        txt_cn = c['trans']
        txt_jp_patched = to_furigana(txt_jp)
        txt_buff_cn.append(txt_cn)
        txt_buff_jp.append(txt_jp_patched)
        end = c['endtime']

    assert len(txt_buff_cn) == 0
    return res


def main():
    key = b'@@www.pep.com.cn'
    lst = []
    for i in range(1, 49):
        print(f'Processing Lesson {i}...')
        lst.extend(process_basic(1, (i-1) // 4 + 1, i, key))
    to_txt(lst, 'output/book1-basic.txt')


if __name__ == '__main__':
    main()
