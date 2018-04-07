"""
Various functions that will be exposed to jinja for use in templates.
"""

import os.path

from app import config

IMG_DIR = '/img'


def get_brand_img(size=256):
    """Get the branding image for the site at the given size."""
    img_name = config.BRAND_IMG.format(size=size)
    img_path = os.path.join(IMG_DIR, img_name)

    return img_path
