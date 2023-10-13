import logging
import os

import openai
import replicate

from insta_gpt.utils import (
    download_image,
    load_topic,
    load_yaml_file,
    publish,
    update_topic
)

# directory path
DIR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# configurations
config = load_yaml_file(os.path.join(DIR_PATH, "config.yaml"))

# logging
logger = logging.getLogger(__name__)


def generate_post():
    topic = load_topic(os.path.join(DIR_PATH, config["topic"]["csv"]))
    caption = generate_caption(topic)
    image_url = generate_image(topic)
    publish(caption, image_url)
    update_topic(os.path.join(DIR_PATH, config["topic"]["csv"]))


def generate_caption(topic):
    prompt = generate_caption_prompt(topic)
    try:
        response = openai.ChatCompletion.create(
            model=config["caption"]["model"],
            messages=[
                {"role": "system", "content": config["caption"]["system_msg"]},
                {"role": "user", "content": prompt}
            ],
            temperature=config["caption"]["temperature"],
        )

        logger.info(f"Generated caption")
        return response.choices[0]["message"]["content"]

    except openai.error.OpenAIError as e:
        logger.error(f"Text generation did not execute: {e.error}")
        logger.warning(f"Http status: {e.http_status}")
        raise e.error


def generate_image(topic):
    prompt = generate_image_prompt(topic)
    if config["scene"]["model"] == "dalle":
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size=config["scene"]["size"]
            )

            logger.info(f"Generated image")
            return response['data'][0]['url']

        except openai.error.OpenAIError as e:
            logger.error(f"Image generation did not execute: {e.error}")
            logger.warning(f"Http status: {e.http_status}")
            raise e.error
    
    elif config["scene"]["model"] == "stable_diffusion":
        width, height = map(int, config["scene"]["size"].split('x'))
        try:
            out = replicate.run(
                "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478",
                input={"prompt": prompt, "width": width, "height": height}
            )

            logger.info(f"Generated image")
            return out[0]

        except replicate.exceptions.ReplicateError as e:
            logger.error(f"Image generation did not execute: {e}")
            raise e

    else:
        model = config["scene"]["model"]
        raise ValueError(f"Selected model {model} is not supported")


def generate_caption_prompt(topic):
    file_path = os.path.join(
        DIR_PATH,
        "insta_gpt",
        "prompt_design",
        "caption_template.txt"
    )
    with open(file_path) as f:
        template = f.read()

    return template + f" The topic of the post is {topic}."


def generate_image_prompt(topic):
    file_path = os.path.join(
        DIR_PATH,
        "insta_gpt",
        "prompt_design",
        "scene_template.txt"
    )
    with open(file_path) as f:
        template = f.read()

    full_template = "photograph, " + template

    return full_template + f" featuring {topic}, realistic, dslr, square"
