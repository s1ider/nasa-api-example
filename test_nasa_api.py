import itertools
import os
import shutil
import unittest
import requests
from glob import glob

from utils import download_photos, compare_images


class TestNasaApiPhotos(unittest.TestCase):
    # usually we should inherit from BaseApiTestCase, where all other basic staff is implemented:
    # read settings, prepare env, init things
    # but there is really no need for that in such simple case
    def setUp(self):
        self.api_key = 'zKyriwJfCEE4UOzuAvdYIQlLSuXWGDNPnB7nQSm2'
        self.base_url = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos'

        # cleanup photos
        shutil.rmtree('./photos')
        os.mkdir('photos')

    def test_photos(self):
        #1 Get first 10 Mars photos made by "Curiosity" on 1000 sol
        params = {
            'api_key': self.api_key,
            'sol': 1000,
        }
        r_sol = requests.get(self.base_url, params=params).json()
        sol_photos = r_sol['photos'][:10]
        img_urls = [photo['img_src'] for photo in sol_photos]
        download_photos(img_urls, 'sol')

        #2 Get the same 10 Mars photos made by "Curiosity" on earth date that is equals 1000 Mars sol
        earth_date_1000_sol = r_sol['photos'][0]['earth_date']
        params = {
            'api_key': self.api_key,
            'earth_date': earth_date_1000_sol,
        }
        r_earth_date = requests.get(self.base_url, params=params).json()
        earth_date_photos = r_earth_date['photos'][:10]
        img_urls = [photo['img_src'] for photo in earth_date_photos]
        download_photos(img_urls, 'earth_date')

        # compare downloaded images
        images = zip(glob('./photos/sol/*'), glob('./photos/earth_date/*'))
        for img in images:
            self.assertTrue(compare_images(*img), msg=img)

        # compare API metadata
        for ind in range(len(sol_photos)):
            self.assertDictEqual(sol_photos[ind], earth_date_photos[ind])

    def test_cameras(self):
        """
        Determine how many pictures were made by each camera (by Curiosity on 1000 sol.)
        If any camera made 10 times more images than any other - test fails.
        """
        curiosity_cameras = ['FHAZ', 'NAVCAM', 'MAST', 'CHEMCAM', 'MAHLI', 'MARDI', 'RHAZ']

        photos_by_camera = {camera: len(self._get_all_photos(1000, camera)) for camera in curiosity_cameras}

        self.assertTrue(all(
            [a / b > 10 or b / 10 > 10
             for a, b in itertools.combinations(photos_by_camera.values(), 2) # get unique pairs of numbers of photos
             if a > 0 and b > 0]
            ), msg=photos_by_camera)

    def _get_all_photos(self, sol, camera):
        params = {
            'api_key': self.api_key,
            'sol': sol,
            'camera': camera,
            'page': 1,
        }
        r = requests.get(self.base_url, params=params).json()
        photos = r['photos']
        while len(r['photos']) == 25:
            params.update({'page': params['page'] + 1})
            r = requests.get(self.base_url, params=params).json()
            photos.append(r['photos'])
        return photos
