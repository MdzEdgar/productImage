from dotenv import dotenv_values
import sys
import os
import time
import requests
import mariadb
from PIL import Image, ImageDraw, ImageFont

config = dotenv_values(".env")


def create_directories():
    if not (os.path.exists('images')):
        os.makedirs('images')

    if not (os.path.exists('processed')):
        os.makedirs('processed')


def download_images(sku_in, url_in):
    sku_fix = sku_in.replace('/', '-')

    response = requests.get(url_in, stream=True)
    time.sleep(0.5)

    if response.status_code == 200:
        with open(f'images/{sku_fix}.jpg', 'wb') as out_file:
            out_file.write(response.content)
    else:
        print(f'No image for {sku_in}.')


def generate_images(sku_in, multiple_in):
    sku_fix = sku_in.replace('/', '-')
    filename = 'images/' + sku_fix + '.jpg'
    newfile = 'processed/' + sku_fix + '.jpg'

    if not (os.path.isfile(filename)):
        print(f'{sku_fix} doesn\'t exist')
    else:
        original = Image.open(filename)
        editable = ImageDraw.Draw(original)

        quantities = str(multiple_in)
        subtext = 'Piezas'
        text = quantities + '\n' + subtext
        font = ImageFont.truetype('Ubuntu-M.ttf', 54)

        textwidth, textheight = editable.textsize(text, font) # noqa
        width, height = original.size
        x = width - (textwidth + 45)
        y = 25

        editable.text((x, y), text, fill="black", font=font, align="center")
        original.save(newfile)


create_directories()

port = int(config['DB_PORT'])
table = config['DB_TABLE']

try:
    connection = mariadb.connect(
        user=config['DB_USER'],
        password=config['DB_PASS'],
        host=config['DB_HOST'],
        port=port,
        database=config['DB_NAME']
    )
except mariadb.Error as err:
    print(f"An error occurred whilst connecting to MariaDB: {err}")
    sys.exit(1)

cursor = connection.cursor()

cursor.execute(f'SELECT codigo, multiplo, imagen FROM {table} WHERE multiplo > ? ', (1, ))

resultCursor = cursor.fetchall()

cursor.close()
connection.close()

for sku, multiple, url in resultCursor:
    download_images(sku, url)
    generate_images(sku, multiple)
