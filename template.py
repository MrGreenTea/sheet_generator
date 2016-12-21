import argparse
import configparser
import itertools
import locale
import os
from datetime import datetime

from PIL import Image
from tqdm import tqdm

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', default=os.getcwd(), help='dir of search for images.', nargs='?')
    parser.add_argument('-r', default=1, dest='repeats', help='Print each file this often.', type=int)
    parser.add_argument('--config', default='config.ini', dest='config', help='use given config')
    parser.add_argument('-d', const=True, default=False, dest='debug', help='enables debug mode', action='store_const')
    parser.add_argument('target_dir', default='print_sheets', help='dir where sheets will be saved in new folder',
                        nargs='?')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    with open(args.config) as config_file:
        config.read_file(config_file)
    section = config['print_sheets']

    WIDTH = section.getint('WIDTH')
    HEIGHT = section.getint('HEIGHT')

    CARD_WIDTH = section.getint('CARD_WIDTH')
    CARD_HEIGHT = section.getint('CARD_HEIGHT')

    CARD_COLUMNS = section.getint('CARD_COLUMNS')
    CARD_ROWS = section.getint('CARD_ROWS')
    CARDS_PER_SHEET = CARD_COLUMNS * CARD_ROWS

    LEFT_MARGIN = section.getint('LEFT_MARGIN')
    TOP_MARGIN = section.getint('TOP_MARGIN')
    SPACING = section.getint('SPACING')

    locale.setlocale(locale.LC_ALL, '')

    if not os.path.exists(args.target_dir):
        os.mkdir(args.target_dir)

    result_dir = os.path.join(args.target_dir, '{:%Y.%m.%d__%X}'.format(datetime.now()))
    os.mkdir(result_dir)

    all_files = sorted(itertools.chain.from_iterable(
        (os.path.join(root, f) for f in files if '.png' in f) for root, _, files in os.walk(args.dir)))

    files_iterator = itertools.chain.from_iterable(itertools.repeat(file, args.repeats) for file in all_files)
    chunked_files = itertools.zip_longest(*[iter(files_iterator)] * CARDS_PER_SHEET)
    coordinates = [(LEFT_MARGIN + x * (CARD_WIDTH + SPACING),
                    TOP_MARGIN + y * (CARD_HEIGHT + SPACING))
                   for y, x in itertools.product(range(CARD_ROWS), range(CARD_COLUMNS))]

    if args.debug:
        empty_image = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), color=(255, 255, 255))
    else:
        empty_image = Image.new('RGB', (1, 1))

    with tqdm(total=len(all_files) * args.repeats) as progress_bar:
        for index, files in enumerate(chunked_files, start=1):
            base_image = Image.new('RGBA' if args.debug else 'RGB', (WIDTH, HEIGHT))

            for pos, file in tqdm(zip(coordinates, files), total=len(files), desc='sheet ' + str(index)):
                if file is None:
                    card_image = empty_image
                else:
                    try:
                        card_image = Image.open(file)
                    except TypeError:
                        print(file)
                        continue
                center_x = card_image.width // 2
                center_y = card_image.height // 2
                crop_box = (center_x - CARD_WIDTH // 2, center_y - CARD_HEIGHT // 2,
                            center_x + CARD_WIDTH // 2, center_y + CARD_HEIGHT // 2)
                if args.debug:
                    card_image = card_image.crop(crop_box)
                else:
                    pos = (pos[0] - crop_box[0], pos[1] - crop_box[1])
                base_image.paste(card_image, box=pos)
                progress_bar.update(1)

            tqdm.write('Saving sheet {}...'.format(index))
            base_image.save(os.path.join(result_dir, '{}.png'.format(index)))
