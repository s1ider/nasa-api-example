import requests
import os
from PIL import Image, ImageChops


def download_photos(urls, folder=''):
    """
    Download photos to local folder with their original names
    :param urls: url to image
    :param folder: optional subfolder
    """
    folder_path = os.path.join('photos', folder)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    for url in urls:
        image = requests.get(url)
        filename = os.path.join(folder_path, url.split('/')[-1])
        with open(filename, 'wb') as f:
            f.write(image.content)


def compare_images(img1_path, img2_path):
    """
    Compares content of two images with PIL
    """
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    try:
        diff = ImageChops.difference(img1, img2)
    except ValueError:
        return False
    return diff.getbbox() is None
