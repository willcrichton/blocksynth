import cv2
import vlc
import random
from time import time
from threading import Thread
from collections import Counter
from Queue import Queue

CALIBRATING = False
TIME_BETWEEN_ROWS = 0.25
NUM_ROWS = 6
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
    'bass',
    'electro',
    'pianobell'
]

queue = Queue()
results = {}
rows = []
frame = None

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

        print rows

        for (instrument, pitch) in cur_row:
            play_sound(instrument, pitch)

        cur_row_index = (cur_row_index + 1) % NUM_ROWS
        last_time = cur_time

def classifyPixel(tuple):
    (blue, green, red) = tuple
    (maximum, middle, minimum) = sorted([blue, green, red], reverse=True)
    if maximum - minimum < 30 or maximum < 1.2 * minimum:
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
                colors.append(classifyPixel(frame[y][x]));

        results[(i, j)] = Counter(colors)
        queue.task_done()

def counts_to_row(counts, pitch):
    row = []
    for index, instrument in enumerate(INSTRUMENTS):
        if counts[index] > 200:
            row.append((instrument, pitch))

    return row

def main():
    for i in range(0, NUM_ROWS):
        rows.append([])

    t = Thread(target=play_music)
    t.daemon = True
    t.start()

    for i in xrange(0, 16):
        t = Thread(target=block_worker)
        t.daemon = True
        t.start()

    camera = cv2.VideoCapture(0)

    global frame
    while True:
        ret, frame = camera.read()

        # Draw grid
        for i in xrange(0,700):
            for j in xrange(0,4):
                frame[i][SQUARE_WIDTH*j] = (0,0,0)
                frame[SQUARE_HEIGHT*j][i] = (0,0,0)

        if not CALIBRATING:
            results.clear()

            # Calculate where our squares are
            for i in xrange(0, NUM_ROWS):
                for j in xrange(0, NUM_COLS):
                    queue.put((i, j))

            queue.join()

            for row in rows:
                del row[:]

            for (i, j), counts in results.iteritems():
                ordered = counts.most_common()
                if ordered[0][0] != SQUARE_WHITE:
                    rows[i].extend(counts_to_row(counts, j + 1))

        # Uncomment the line below to see the feed
        cv2.imshow('video', frame)

    del(camera)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
