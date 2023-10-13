from dotenv import load_dotenv
import io
import logging
import os
import pandas as pd
from PIL import Image
from urllib3.exceptions import HTTPError
import requests
from requests.exceptions import ProxyError
import yaml

from instagrapi import Client
from instagrapi.exceptions import (
    GenericRequestError, 
    ClientConnectionError,
    PhotoNotUpload,
)
import openai


DIR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_PATH = os.path.join(DIR_PATH, "temp.jpg")

logger = logging.getLogger(__name__)


def download_image(url, save_path):
    response = requests.get(url)
    image = Image.open(io.BytesIO(response.content))

    # Convert the image to RGB format if it has an alpha channel
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    # Save the image as JPEG
    image.save(save_path, 'JPEG')
    logger.info(f"Image downloaded and saved as {save_path}")


def setup_logging():
    logging.basicConfig(level=logging.INFO)

    # Create a FileHandler and set its output file
    file_handler = logging.FileHandler(
        os.path.join(DIR_PATH, "application.log"))
    file_handler.setLevel(logging.INFO)

    # Define a formatter for the file handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the root logger
    logging.getLogger('').addHandler(file_handler)


def setup():
    load_dotenv()
    setup_logging()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    logger.info("Initialized")


def publish(caption, image_url):
    # TODO: use native instagram api in order to post from image url
    # save image in order to post image via instagrapi
    download_image(image_url, TMP_PATH)

    try: 
        cl = Client()
        cl.login(os.getenv("USER_ID"), os.getenv("PASSWORD"))
    except (ProxyError, HTTPError, GenericRequestError, ClientConnectionError) as e:
        logger.error(f"Network Error: {e}, retry with different proxy")
        raise

    try:
        media = cl.photo_upload(
            TMP_PATH,
            caption
        )
        logger.info("Successfully published on Instagram")
        os.remove(TMP_PATH)
    except PhotoNotUpload:
        os.remove(TMP_PATH)
        logger.error("Could not upload the photo")
        raise

def load_yaml_file(file_path):
    with open(file_path, 'r') as file:
        try:
            config = yaml.safe_load(file)
            return config
        except yaml.YAMLError as e:
            logger.error(f"Error loading YAML file {file_path}")
            raise yaml.YAMLError(f"Error loading YAML file {file_path}")


def load_topic(filename):
    df = pd.read_csv(filename, header=0)
    if not df["posted"].all():
        if len(df[~df["posted"]]) < 5:
            logger.warning(f"Only {len(df[~df['posted']])} topics from "
                           f"{filename} left for posting")
        return df.loc[~df["posted"], "topic"].iloc[0]
    else:
        logger.error(f"All topics from {filename} are posted")
        raise ValueError(f"All topics from {filename} are posted")


def update_topic(filename):
    df = pd.read_csv(filename, header=0)
    row_index = df.loc[~df["posted"], :].index[0]
    df.loc[row_index, "posted"] = True
    df.to_csv(filename, index=False)
    logger.info(f"Updated {filename} - Marked topic as posted")
