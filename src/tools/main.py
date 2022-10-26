import re

import aiohttp
import naff
from algoliasearch.search_client import SearchClient
from dateutil.parser import isoparse

DISAMBIGUATION_CAT = "Category:All disambiguation pages"
WHITESPACE = re.compile(r"[\n\s]{4,}")
NEWLINES = re.compile(r"\n+")


def __init__(self, bot):
    self.bot = bot
    ## Fill out from trying a search on the ddevs portal
    app_id = "BH4D9OD16A"
    api_key = "f37d91bd900bbb124c8210cca9efcc01"
    self.search_client = SearchClient.create(app_id, api_key)
    self.index = self.search_client.init_index("discord")


def generate_payload(query: str):
    """Generate the payload for Wikipedia based on a query string."""
    query_tokens = query.split()
    payload = {
        # Main module
        "action": "query",  # Fetch data from and about MediaWiki
        "format": "json",  # Output data in JSON format
        # format:json options
        "formatversion": "2",  # Modern format
        # action:query options
        "generator": "search",  # Get list of pages by executing a query module
        "redirects": "1",  # Automatically resolve redirects
        "prop": "extracts|info|pageimages|revisions|categories",  # Which properties to get
        # action:query/generator:search options
        "gsrsearch": f"intitle:{' intitle:'.join(query_tokens)}",  # Search for page titles
        # action:query/prop:extracts options
        "exintro": "1",  # Return only content before the first section
        "explaintext": "1",  # Return extracts as plain text
        # action:query/prop:info options
        "inprop": "url",  # Gives a full URL for each page
        # action:query/prop:pageimages options
        "piprop": "original",  # Return URL of page image, if any
        # action:query/prop:revisions options
        "rvprop": "timestamp",  # Return timestamp of last revision
        # action:query/prop:revisions options
        "clcategories": DISAMBIGUATION_CAT,  # Only list this category
    }
    return payload


async def perform_search(query, only_first_result: bool = False):
    """Query Wikipedia."""
    payload = generate_payload(query)
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://en.wikipedia.org/w/api.php",
            params=payload,
            headers={"user-agent": "Mozilla/5.0"},
        ) as res:
            result = await res.json()

    embeds = []
    if "query" in result and "pages" in result["query"]:
        result["query"]["pages"].sort(key=lambda unsorted_page: unsorted_page["index"])
        for page in result["query"]["pages"]:
            try:
                if (
                    "categories" in page
                    and page["categories"]
                    and "title" in page["categories"][0]
                    and page["categories"][0]["title"] == DISAMBIGUATION_CAT
                ):
                    continue  # Skip disambiguation pages
                embeds.append(generate_embed(page))
                if only_first_result:
                    return embeds, page["fullurl"]
            except KeyError:
                pass
    return embeds, None


def generate_embed(page_json):
    """Generate the embed for the json page."""
    title = page_json["title"]
    description: str = page_json["extract"].strip()
    image = (
        page_json["original"]["source"]
        if "original" in page_json and "source" in page_json["original"]
        else None
    )
    url = page_json["fullurl"]
    timestamp = (
        isoparse(page_json["revisions"][0]["timestamp"])
        if "revisions" in page_json
        and page_json["revisions"]
        and "timestamp" in page_json["revisions"][0]
        else None
    )

    whitespace_location = None
    whitespace_check_result = WHITESPACE.search(description)
    if whitespace_check_result:
        whitespace_location = whitespace_check_result.start()
    if whitespace_location:
        description = description[:whitespace_location].strip()
    description = NEWLINES.sub("\n\n", description)
    if len(description) > 1000 or whitespace_location:
        description = description[:1000].strip()
        description += f"... [(read more)]({url})"

    embed = naff.Embed(
        title=f"Wikipedia: {title}",
        description=description,
        color=0x0083F5,
        url=url,
        timestamp=timestamp,
    )
    if image:
        embed.set_image(url=image)
    text = "Information provided by Wikimedia"
    if timestamp:
        text += "\nArticle last updated"
    embed.set_footer(
        text=text,
        icon_url=(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Wikimedia-logo.png"
            "/600px-Wikimedia-logo.png"
        ),
    )
    return embed


def beaufort_scale(speed):
    """Converts a wind speed in m/s to a Beaufort scale number."""
    if speed < 0:
        return "I don't fucking know"
    elif speed <= 0.3:
        return "Calm"
    elif speed <= 1.5:
        return "Light air"
    elif speed <= 3.3:
        return "Light breeze"
    elif speed <= 5.5:
        return "Gentle breeze"
    elif speed <= 7.9:
        return "Moderate breeze"
    elif speed <= 10.7:
        return "Fresh breeze"
    elif speed <= 13.8:
        return "Strong breeze"
    elif speed <= 17.1:
        return "Moderate gale"
    elif speed <= 20.7:
        return "Gale"
    elif speed <= 24.4:
        return "Strong gale"
    elif speed <= 28.4:
        return "Storm"
    elif speed <= 32.6:
        return "Violent storm"
    else:
        return "Hurricane force"


def pretty_weather(weather):
    """Converts a weather object into a human readable string."""
    weather = weather.lower()
    if weather == "light rain":
        return "Light rain"
    elif weather == "snow":
        return "Snow"
    elif weather == "light intensity drizzle":
        return "Light intensity drizzle"
    elif weather == "light snow":
        return "Light snow"
    elif weather == "broken clouds":
        return "Broken clouds"
    elif weather == "clear sky":
        return "Clear sky"
    elif weather == "haze":
        return "Haze"
    elif weather == "overcast clouds":
        return "Overcast clouds"
    elif weather == "mist":
        return "Mist"
    elif weather == "few clouds":
        return "Few clouds"
    elif weather == "scattered clouds":
        return "Scattered clouds"
    elif weather == "moderate rain":
        return "Moderate rain"
    elif weather == "shower rain":
        return "Shower rain"
    else:
        return weather.capitalize()


def guild_av(member):
    """
    Returns a member guild avatar.
    Args:
        member: naff.Member() object
    """
    return member.guild_avatar.url


def av(member):
    """
    Returns a member avatar.
    Args:
        member: naff.Member() object
    """
    return user.avatar.url
