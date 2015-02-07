import cv2
import vlc
import random
from time import time
from threading import Thread
from collections import Counter

TIME_BETWEEN_ROWS = 0.25
NUM_ROWS = 100
NUM_SAMPLES = 16

INSTRUMENTS = [
    'bass',
    'bell',
    'corny',
    'drums',
    'electro',
    'pianobell',
    'woody'
]

rows = []

def play_sound(instrument, pitch):
    path = 'sounds/%s_%s.mp3' % (instrument, pitch)
    vlc.MediaPlayer(path).play()

def play_music():
    last_time = time()
    cur_row_index = 0

    while True:
        cur_time = time()
        delta = cur_time - last_time

        if delta < TIME_BETWEEN_ROWS: continue
        cur_row = rows[cur_row_index]

        for (instrument, pitch) in cur_row:
            play_sound(instrument, pitch)

        cur_row_index = (cur_row_index + 1) % NUM_ROWS
        last_time = cur_time

def classifyPixel(tuple):
    (blue, green, red) = tuple
    (maximum, middle, minimum) = sorted([blue, green, red], reverse=True)
    if maximum - minimum < 30:
        return "white"
    elif maximum == blue:
        return "blue"
    elif maximum == red:
        return "red"
    else:
        return "green"


def main():
    for i in range(0, NUM_ROWS):
        rows.append([])

    t = Thread(target=play_music)
    t.daemon = True
    t.start()

    camera = cv2.VideoCapture(0)

    while True:
        ret, frame = camera.read()
        print frame[173*2][170*2]
        print classifyPixel(frame[173*2][170*2])
        for i in xrange(0,700):
            for j in xrange(0,4):
                frame[i][170*j] = (0,0,0)
                frame[173*j][i] = (0,0,0)
        colors = []
        for r in xrange(2*173,3*173):
            for c in xrange(2*170,3*170):
                pass
                #colors.append(classifyPixel(frame[r][c]))
        counter = Counter(colors)
        print counter        
        height = len(frame)
        width = len(frame[0])


        # Uncomment the line below to see the feed
        cv2.imshow('video', frame)

    del(camera)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
