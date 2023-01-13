|Discord Server| Deploy CI | Docker CI | pre-commit | Style |
| :---:  | :---: | :---:               | :---: | :---: |
| [![Discord server](https://img.shields.io/discord/922523614828433419?label=Join%20our%20Discord%20Server%21)](https://warunginternational.eu.org) | [![Deploy to Fly.io](https://github.com/warung-international/peradaban/actions/workflows/deploy.yml/badge.svg)](https://github.com/warung-international/peradaban/actions/workflows/deploy.yml) |[![Build Production](https://github.com/warung-international/peradaban/actions/workflows/build.yml/badge.svg)](https://github.com/warung-international/peradaban/actions/workflows/build.yml)  | [![precommit](https://github.com/warung-international/peradaban/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/warung-international/peradaban/actions/workflows/pre-commit.yml) | [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) |

-------------------------------------------------


# Peradaban

> OwO, What's this?

Peradaban is a Discord Server Bots made with [NAFF](https://github.com/NAFTeam/NAFF) (python) designed only for Warung International.

Visit [the official guide](https://naff.info/Guides/01%20Getting%20Started.html) to get started.

## Development

This project is open to anyone who wants to contribute, large or small! Whether you noticed a typo or want to add a whole new feature, go for it!

Large additions should be discussed in issues or on Discord first. If you're new to Python, ask me on [Discord](https://discord.com/users/351150966948757504) for where to start and you can use Peradaban as a starting point for a contribution.

Also, Please note that this code is _Production Ready_. It means, this code is a live source code of our discord server bot.

## Testing/Workflow

To run the app, you need:

- A Discord server to test - you can't use the Warung International Discord Server to do tests
- Python 3.11.1 - no guarantees on older versions
- A Discord bot with the 'Message Intent', 'Server Members Intent', and 'Presence Intent' enabled
- MongoDB Server, or MongoDB Atlas.

If you don't own/admin a Discord server, creating one is simple, you can do it from the same menu you join discord servers from.

## Running the Application
There are multiple ways to launch the application.

### Python
To start the bot with python, you first need to install the required packages with `pip install -r requirements.txt`

Then, run:

```bash
python main.py
```


### Docker-Compose
You can use the pre-made Docker Compose by running:

```bash
docker-compose up
```

### Docker
For most users, the use of `docker-compose` is highly recommended.

Nevertheless, you can import the pre-made Dockerfile into your own docker-compose or run it manually by with:

```bash
docker build -t peradaban .

docker run -it peradaban
```

Note: Make sure that you created a volume so that you local `./logs` folder gets populated.

## Additional Information

Additionally, this comes with a pre-made [pre-commit](https://pre-commit.com) config to keep your code clean.

It is recommended that you set this up by running:

```bash
pip install pre-commit

pre-commit install
```

## Awesome

Awesome projects that i take reference from, credits to all of them :3

- [siren15/Melody](https://github.com/siren15/Melody)
- [NAFTeam/Dis-Secretary](https://github.com/NAFTeam/Dis-Secretary)
