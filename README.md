# Automated social media manager
This is an experimental automated social media manager, showcasing capabilities of large language and 
text-to-image models for content creation. 

![alt text](docs/imgs/example.png "image Title")


Note: Currently the text-to-image engine uses OpenAI's Dall-E. In the next version, it is possible to choose between the 
engines Dall-E, Stable Diffusion and Midjourney.

## Installation

This code was tested with Python 3.9.7 and poetry 1.5.1.

### Getting an API key
 Get an OpenAI [API Key](https://platform.openai.com/account/api-keys).

### Setup 
1. Clone the repository

```
git clone 
```

2. Install project dependencies using poetry:
```
cd social-media-manager
poetry install
```

### Configuration

1. Find the file named `.env.template` in the main folder. This file may
    be hidden by default in some operating systems due to the dot prefix.
2. Create a copy of `.env.template` and call it `.env`;
    if you're already in a command prompt/terminal window: `cp .env.template .env`.
3. Open the `.env` file in a text editor.
4. Find the line that says `OPENAI_API_KEY=`.
5. After the `=`, enter your unique OpenAI API Key *without any quotes or spaces*.
6. Find the lines that say `USER_ID=` and `PASSWORD=`.
7. After the `=`, enter your unique Instagram credentials *without any quotes or spaces*.
8. Save and close the `.env` file.

## Usage

### Configurations
1. Create a csv file with the topics you want to be 
posted and save in the directory. The csv format should follow:
```
topic,posted
blueberry,False
strawberry,False
raspberry,False
```
2. Adapt the prompt design for your needs. The prompt templates for caption and scene generation are located at `social_media_manager/prompt_design`. 
Sources for best practices in prompt engineering are for example [reddit](https://www.reddit.com/r/PromptEngineering/) 
and [openai docs](https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-openai-api).
3. Adapt the `config.yaml` file with the filename of the csv and openai related configurations. Currently, it is [best 
practice](https://platform.openai.com/docs/guides/gpt) to use the "gpt-3.5-turbo" model, because of the cost and 
performance. If an increase in performance is required, "gpt-4" model can also be set. Note that
the [pricing](https://openai.com/pricing) of "gpt-4" is by far higher.

### Run
You can run the script `main.py` using Python:

```
poetry run python main.py
```

If operating on a Linux or MacOS system, the script can also be scheduled to run with cronjobs by adding an entry to the crontab file.

```
sudo crontab -u $(whoami) -e
```

Details on schedule expressions can be found on [crontab.guru](https://crontab.guru/). Cronjob does need absolute 
paths. To get the path of python in poetry, run the command `poetry run which python`.

```
# Run the script every day at 9:00 AM
0 9 * * * /path/to/poetry/python /path/to/social-media-manager/main.py >> /path/to/social-media-manager/cron.log 2>&1
```

To end a cronjob, edit the crontab file or kill the cronjob:
```
crontab -r
```

## Disclaimer
Please note that the use of a GPT language model and text-to-image models can be expensive due to its token usage. By utilizing this project, 
you acknowledge that you are responsible for monitoring and managing your own token usage and the associated costs. It 
is highly recommended to check your OpenAI API usage regularly and set up any necessary limits or alerts to prevent unexpected charges.