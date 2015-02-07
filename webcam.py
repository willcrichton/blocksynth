import cv2
import vlc
import random
from time import time
from threading import Thread

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

def play_music():
    cur_time = time()
    while True:
        next_time = time()
        delta = next_time - cur_time

        # TODO: play musak

        cur_time = next_time

def main():
    t = Thread(target=play_music)
    t.daemon = True
    t.start()

    camera = cv2.VideoCapture(0)

    while True:
        ret, frame = camera.read()
        height = len(frame)
        width = len(frame[0])

        # Uncomment the line below to see the feed
        # cv2.imshow('video', frame)

    del(camera)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()