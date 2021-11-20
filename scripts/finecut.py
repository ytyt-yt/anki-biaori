from glob import glob

from pydub import AudioSegment
import audioop


def get_avg(audio, start, end):
    return abs(audioop.avg(audio[start:end]._data, audio.sample_width))


def cut(filename, ms):
    audio = AudioSegment.from_mp3(filename)
    audio[ms:].export(filename.replace('audio/', 'audio-finecut/'))


def finecut(filename, skip=0):
    audio = AudioSegment.from_mp3(filename)
    idx = skip
    while idx < 2000 and get_avg(audio, idx, idx+100) > 1:
        idx += 50
    while idx < 2000 and get_avg(audio, idx, idx+100) <= 1:
        idx += 50
    if idx < 2000:
        audio = audio[idx:]
    print(f'Cut {filename}: {idx}ms')
    audio.export(filename.replace('audio/', 'audio-finecut/'))


def main():
    fs = glob('./output/audio/*.mp3')
    for f in sorted(fs):
        finecut(f)

    finecut('./output/audio/book1-lesson01-basic-A.mp3', 1000)
    finecut('./output/audio/book1-lesson01-basic-D.mp3', 300)
    finecut('./output/audio/book1-lesson02-basic-A.mp3', 300)
    finecut('./output/audio/book1-lesson18-basic-A.mp3', 300)
    finecut('./output/audio/book1-lesson24-basic-C.mp3', 300)
    finecut('./output/audio/book1-lesson37-basic-C.mp3', 1000)
    finecut('./output/audio/book1-lesson41-basic-C.mp3', 1000)
    finecut('./output/audio/book1-lesson46-basic-4.mp3', 300)
    finecut('./output/audio/book1-lesson46-basic-A.mp3', 300)
    finecut('./output/audio/book1-lesson47-basic-A.mp3', 300)
    finecut('./output/audio/book1-lesson48-basic-B.mp3', 1000)

    cut('./output/audio/book1-lesson04-basic-C.mp3', 0)
    cut('./output/audio/book1-lesson08-basic-1.mp3', 0)
    cut('./output/audio/book1-lesson08-basic-2.mp3', 0)
    cut('./output/audio/book1-lesson11-basic-2.mp3', 0)
    cut('./output/audio/book1-lesson13-basic-B.mp3', 0)
    cut('./output/audio/book1-lesson17-basic-1.mp3', 0)
    cut('./output/audio/book1-lesson28-basic-3.mp3', 0)
    cut('./output/audio/book1-lesson28-basic-4.mp3', 0)
    cut('./output/audio/book1-lesson34-basic-D.mp3', 0)
    cut('./output/audio/book1-lesson36-basic-B.mp3', 0)

    cut('./output/audio/book1-lesson46-basic-D.mp3', 800)


if __name__ == '__main__':
    main()
