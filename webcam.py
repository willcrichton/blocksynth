import cv2
import vlc
import random
from time import time, sleep
from threading import Thread
from collections import Counter
from Queue import Queue
import numpy as np
import sys

CALIBRATING = int(sys.argv[1])
BEAT_TIME = 0.25
NUM_ROWS = 8
NUM_COLS = 4
NUM_SAMPLES = 16
SQUARE_WIDTH = 170
SQUARE_HEIGHT = 173
SQUARE_RED = 0
SQUARE_GREEN = 1
SQUARE_BLUE = 2
SQUARE_WHITE = 3

'''
INSTRUMENTS = [
    'bass',
    'bell',
    'corny',
    'drums',
    'electro',
    'pianobell',
    'woody'
]
'''

INSTRUMENTS = [
    'pianobell',
    'pianobell',
    'pianobell'
]

queue = Queue()
results = {}
rows = []
frame = None

def play_sound(instrument, pitch):
    path = 'sounds/%s_%s.mp3' % (instrument, pitch)
    player = vlc.MediaPlayer(path)
    player.audio_set_volume(200)
    player.play()

def play_music():
    last_time = time()
    cur_row_index = 0
    cur_beat = 0

    while True:
        cur_time = time()
        delta = cur_time - last_time

        if delta < BEAT_TIME: continue

        if cur_beat % 2 == 0:
            if cur_beat == 6:
                play_sound('drums', 2)
                play_sound('bass', 5)
            else:
                play_sound('drums', 2)
                play_sound('bass', 2)

        cur_beat = (cur_beat + 1) % 8
        cur_row = rows[cur_row_index]

        for (instrument, pitch) in cur_row:
            play_sound(instrument, pitch)

        cur_row_index = (cur_row_index + 1) % NUM_ROWS
        last_time = cur_time

def classifyPixel(tuple):
    (blue, green, red) = tuple
    (maximum, middle, minimum) = sorted([blue, green, red], reverse=True)
    if maximum - minimum < 30 or maximum < minimum * 1.2:
        return SQUARE_WHITE
    elif maximum == blue:
        return SQUARE_BLUE
    elif maximum == red:
        return SQUARE_RED
    else:
        return SQUARE_GREEN

def block_worker():
    while True:
        (i, j) = queue.get()
        colors = []
        for x in xrange(i * SQUARE_WIDTH, (i + 1) * SQUARE_WIDTH, 4):
            for y in xrange(j * SQUARE_HEIGHT, (j + 1) * SQUARE_HEIGHT, 4):
                color = classifyPixel(frame[y][x])

                if color != SQUARE_WHITE:
                    colors.append(color);

        results[(i, j)] = Counter(colors)
        queue.task_done()

def counts_to_row(counts, pitch):
    row = []
    for index, instrument in enumerate(INSTRUMENTS):
        if counts[index] > 200:
            row.append((instrument, pitch))

    return row

def spawn_thread(func):
    t = Thread(target=func)
    t.daemon = True
    t.start()

def main():
    global rows

    for i in range(0, NUM_ROWS):
        rows.append([])

    spawn_thread(play_music)

    for i in xrange(0, 8):
        spawn_thread(block_worker)

    camera = cv2.VideoCapture(0)

    global frame
    while True:
        ret, frame = camera.read()

        frame = cv2.medianBlur(frame, 5)

        if not CALIBRATING:
            results.clear()

            # Calculate where our squares are
            for i in xrange(0, NUM_ROWS):
                for j in xrange(0, NUM_COLS):
                    queue.put((i, j))

            queue.join()

            new_rows = []
            for i in range(0, NUM_ROWS):
                new_rows.append([])

            for (i, j), counts in results.iteritems():
                ordered = counts.most_common()
                if len(ordered) > 0 and ordered[0][1] > 300 and (ordered[0][0] != SQUARE_GREEN or ordered[0][1] > 550 or (len(ordered) > 1 and ordered[0][1] - ordered[1][1] < 200)):
                    #print (i, j), map(lambda (n, c): ('red' if n == SQUARE_RED else ('blue' if n == SQUARE_BLUE else 'green'), c), ordered)
                    new_rows[i].extend(counts_to_row(counts, j + 1))

            rows = new_rows

            #print ''

            sleep(0.5)

        else:
            # Draw grid
            for i in xrange(0,NUM_COLS):
                for j in xrange(0, len(frame[0])):
                    frame[i * SQUARE_HEIGHT][j] = (0,0,0)

            for j in xrange(0, NUM_ROWS):
                for i in xrange(0, len(frame)):
                    frame[i][j * SQUARE_WIDTH] = (0,0,0)

            cv2.imshow('video', frame)

    del(camera)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
