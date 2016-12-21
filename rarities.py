import itertools
import os
import shutil

from PIL import Image
from tqdm import tqdm

all_pngs = list(itertools.chain.from_iterable(
    (os.path.join(root, f) for f in files if '.png' in f) for root, _, files in os.walk('[SW] Star Wars The Gathering')
))


POS = 725, 675
rarity_map = {(0, 0, 0): 'common', (181, 207, 223): 'uncommon', (246, 150, 29): 'mythic', (214, 188, 115): 'rare'}
# colors at POS and their rarity. Not very reliable.


for file in tqdm(all_pngs):
    im = Image.open(file)
    color = im.getpixel(POS)
    try:
        folder = rarity_map[color]
    except KeyError:
        if 'Basic Land' in file:
            shutil.copy2(file, 'rarities/basic_lands/')
        elif 'Token' in file:
            shutil.copy2(file, 'rarities/tokens/')
        else:
            shutil.copy2(file, 'rarities/rest/')
    else:
        shutil.copy2(file, 'rarities/{}/'.format(folder))
