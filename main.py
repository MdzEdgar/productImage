from dotenv import dotenv_values
import sys
import os
import time
import requests
import mariadb

config = dotenv_values(".env")


def create_directory():
    if not (os.path.exists('images')):
        os.makedirs('images')


def download_images(sku_in, url_in):
    sku_fix = sku_in.replace('/', '-')

    response = requests.get(url_in, stream=True)
    time.sleep(0.5)

    if response.status_code == 200:
        with open(f'images/{sku_fix}.jpg', 'wb') as out_file:
            out_file.write(response.content)
    else:
        print(f'No image for {sku_in}.')


create_directory()

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

cursor.execute(f'SELECT codigo, multiplo, imagen FROM {table} WHERE multiplo > ? LIMIT 10', (1, ))

resultCursor = cursor.fetchall()

cursor.close()
connection.close()

for sku, multiple, url in resultCursor:
    download_images(sku, url)

