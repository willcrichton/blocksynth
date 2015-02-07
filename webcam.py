import cv2
import vlc
import random
from time import sleep
from threading import Thread
from Queue import Queue

queue = Queue()

instruments = [
    'bass',
    'bell',
    'corny',
    'drums',
    'electro',
    'pianobell',
    'woody'
]

def play_sound(instrument, pitch):
    path = 'sounds/%s_%s.mp3' % (instrument, pitch)
    vlc.MediaPlayer(path).play()

def analyze_frames():
    while True:
        frame = queue.get()
        height = len(frame)
        width = len(frame[0])

        # TODO: process the frame

        queue.task_done()

def main():
    t = Thread(target=analyze_frames)
    t.daemon = True
    t.start()

    camera = cv2.VideoCapture(0)

    while True:
        ret, frame = camera.read()

        # Uncomment the line below to see the feed
        # cv2.imshow('video', frame)

        queue.put(frame)

    del(camera)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()