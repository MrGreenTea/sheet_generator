import itertools
import os

import shutil
from PIL import Image

all_files = list(itertools.chain.from_iterable((os.path.join(root, f) for f in files if '.png' in f) for root, _, files in os.walk('[SW] Star Wars The Gathering')))


rd = {(0, 0, 0): 'common', (181, 207, 223): 'uncommon', (246, 150, 29): 'mythic', (214, 188, 115): 'rare'}

POS = 725, 675

for file in all_files:
    im = Image.open(file)
    color = im.getpixel(POS)
    try:
        folder = rd[color]
    except KeyError:
        if 'Basic Land' in file:
            shutil.copy2(file, 'rarities/basic_lands/')
        elif 'Token' in file:
            shutil.copy2(file, 'rarities/tokens/')
        else:
            print(file, color)
            shutil.copy2(file, 'rarities/rest/')
    else:
        shutil.copy2(file, 'rarities/{}/'.format(folder))
