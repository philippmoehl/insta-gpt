import logging
import openai
import os

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
    try:
        logger.info(f"Generating content for topic {topic}")
        caption = generate_caption(topic)
        logger.info(f"Generated caption")
        image_url = generate_image(topic)
        logger.info(f"Generated image")
        publish(caption, image_url)
        update_topic(os.path.join(DIR_PATH, config["topic"]["csv"]))
    except Exception as e:
        logger.error(str(e))
        raise ValueError(str(e))


def generate_caption(topic):
    prompt = generate_caption_prompt(topic)
    response = openai.ChatCompletion.create(
        model=config["caption"]["model"],
        messages=[
            {"role": "system", "content": config["caption"]["system_msg"]},
            {"role": "user", "content": prompt}
        ],
        temperature=config["caption"]["temperature"],
    )

    return response.choices[0]["message"]["content"]


def generate_image(topic):
    prompt = generate_image_prompt(topic)
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size=config["scene"]["size"]
    )

    return response['data'][0]['url']


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
