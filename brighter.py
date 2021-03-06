import numpy as np
import cv2
from PIL import Image, ImageEnhance
import subprocess
import os
import sys
import shutil
import argparse

"""
Creates a brighter video using ffmpeg. Requires ffmpeg and opencv 3x. 
Supports mp4 and avi formats.

Usage: $python brighter.py -i video.mp4 -o newvideo.mp4 --brightness 2
"""

parser = argparse.ArgumentParser(description='Brighter.py', version='0.1')

parser.add_argument('-i', '--input', dest='input_name', type=str, required=True, 
                    help="Path, name and filetype of video to make brighter")
parser.add_argument('-o', '--output', dest='output_name', type=str, 
                    default='brighter.avi', 
                    help="Path, name and filetype of output file")
parser.add_argument('-b', '--brightness', dest='brightness', type=str, default=3, 
                    help="A number from 1-9 where 1 is the current brightness")

parsed = parser.parse_args()
input_name = parsed.input_name
output_name = parsed.output_name
brightness = parsed.brightness

if input_name.endswith('mp4') or input_name.endswith('avi'):
    video = input_name
else:
    print("This script currently supports mp4 and avi formats only.")
    sys.exit(1)

try:
    subprocess.check_output(['which','ffmpeg'])
except:
    print("Please install ffmpeg or add it to your bash profile.")
    sys.exit(1)

def create_tempdir():
    try:
        os.mkdir('./temp/')
    except OSError, e:
        print(e)


def extract_audio(input_name):
    args = ['ffmpeg',
        '-i', '{}'.format(input_name),
        '-ab', '160k', 
        '-ac', '2', 
        '-ar', '44100', 
        '-vn', './temp/{}wav'.format(input_name[:-3])]
    
    try:
        p = subprocess.call(args)
    except:
        print("Failed to extract audio.")
        sys.exit(1)


def load_video(video):
    cap = cv2.VideoCapture(video)
    if not cap:
        print("Failed to load video.")
        sys.exit(1)
    fps = cap.get(cv2.CAP_PROP_FPS)
    return cap, fps


def frames_to_png(cap, brightness):
    f = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret==True:
            f += 1

            # Convert cv2 image to rgb and load from numpy array
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)

            # Enhance brightness
            img = ImageEnhance.Brightness(img)
            img = img.enhance(int(brightness))

            # Convert back to bgr numpy array and write to disk
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            cv2.imwrite('./temp/frame{}.png'.format(str(f)),frame)
        else:
            break
    cap.release()


def png_to_mp4(framerate):
    framerate = str(framerate)
    
    args = ["ffmpeg",
        "-framerate", framerate,
        "-r", framerate,
        "-i","./temp/frame%d.png",
        "-vcodec","png",
        "./temp/0vid.mp4"]

    try:
        p = subprocess.call(args)
    except Exception, e:
        print(e)
        print("Failed to convert pngs to mp4.")
        sys.exit(1)


def make_avi():
    args = [
        "ffmpeg",
        "-i","./temp/0vid.mp4",
        "-i","./temp/{}wav".format(input_name[:-3]),
        "-vcodec","copy",
        "-acodec","copy",
        "{}avi".format(output_name[:-3])
    ]

    try:
        p = subprocess.call(args)
    except:
        print("Failed to make avi.")
        sys.exit(1)


def make_mp4():
    args = [
        "ffmpeg",
        "-i","{}avi".format(output_name[:-3]),
        "-b:a","128k",
        "-vcodec","mpeg4",
        "-b:v","1200k",
        "-flags","+aic+mv4",
        output_name
    ]

    try:
        p = subprocess.call(args)
    except:
        print("Failed to make mp4.")
        sys.exit(1)


def cleanup():
    try:
        shutil.rmtree('./temp')
    except:
        print("Failed to clean up temp directory.")


def main():
    create_tempdir()
    extract_audio(video)
    stream, framerate = load_video(video)
    frames_to_png(stream, brightness)
    png_to_mp4(framerate)
    make_avi()
    if output_name.endswith('mp4'):
        make_mp4()
        os.remove('{}avi'.format(output_name[:-3]))
    cleanup()


if __name__ == '__main__':
    main()
