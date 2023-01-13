import random
import urllib.parse

smallcaps_alphabet = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ1234567890"

uppercase_fraktur = "𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ"
lowercase_fraktur = "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷1234567890"

uppercase_boldfraktur = "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅"
lowercase_boldfraktur = "𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟1234567890"


double_uppercase = "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"

double_lowercase = "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡𝟘"

bold_fancy_lowercase = "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃1234567890"
bold_fancy_uppercase = "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩"

fancy_lowercase = "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫𝟢"
fancy_uppercase = "𝒜𝐵𝒞𝒟𝐸𝐹𝒢𝐻𝐼𝒥𝒦𝐿𝑀𝒩𝒪𝒫𝒬𝑅𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"


alphabet = dict(zip("abcdefghijklmnopqrstuvwxyz1234567890", range(0, 36)))
uppercase_alphabet = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", range(0, 26)))
punctuation = dict(zip("§½!\"#¤%&/()=?`´@£$€{[]}\\^¨~'*<>|,.-_:", range(0, 37)))
space = " "
aesthetic_space = "\u3000"
aesthetic_punctuation = '§½！"＃¤％＆／（）＝？`´＠£＄€｛［］｝＼＾¨~＇＊＜＞|，．－＿：'
aesthetic_lowercase = "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ１２３４５６７８９０"
aesthetic_uppercase = "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"

eight_ball_responses = [
    "It is certain",
    "It is decidedly so",
    "Without a doubt",
    "Yes, definitely",
    "You may rely on it",
    "As I see it, yes",
    "Most likely",
    "Outlook good",
    "Yes",
    "Signs point to yes",
    "Reply hazy try again",
    "Ask again later",
    "Better not tell you now",
    "Cannot predict now",
    "Concentrate and ask again",
    "Don't count on it",
    "My reply is no",
    "My sources say no",
    "Outlook not so good",
    "Very doubtful",
]

KAOMOJI_JOY = [
    " (\\* ^ ω ^)",
    " (o^▽^o)",
    " (≧◡≦)",
    ' ☆⌒ヽ(\\*"､^\\*)chu',
    " ( ˘⌣˘)♡(˘⌣˘ )",
    " xD",
]
KAOMOJI_EMBARRASSED = [
    " (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)..",
    " (\\*^.^\\*)..,",
    "..,",
    ",,,",
    "... ",
    ".. ",
    " mmm..",
    "O.o",
]
KAOMOJI_CONFUSE = [" (o_O)?", " (°ロ°) !?", " (ーー;)?", " owo?"]
KAOMOJI_SPARKLES = [" \\*:･ﾟ✧\\*:･ﾟ✧ ", " ☆\\*:・ﾟ ", "〜☆ ", " uguu.., ", "-.-"]


def aesthetics(string):
    """Convert a string to aesthetics."""
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += aesthetic_lowercase[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += aesthetic_uppercase[uppercase_alphabet[letter]]
            elif letter in punctuation:
                returnthis += aesthetic_punctuation[punctuation[letter]]
            elif letter == space:
                returnthis += aesthetic_space
            else:
                returnthis += letter
    return returnthis


def double_font(string):
    """Convert a string to double font."""
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += double_lowercase[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += double_uppercase[uppercase_alphabet[letter]]
            elif letter == space:
                returnthis += " "
            else:
                returnthis += letter
    return returnthis


def fraktur(string):
    """Convert a string to fraktur."""
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += lowercase_fraktur[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += uppercase_fraktur[uppercase_alphabet[letter]]
            elif letter == space:
                returnthis += " "
            else:
                returnthis += letter
    return returnthis


def bold_fraktur(string):
    """Convert a string to bold fraktur."""
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += lowercase_boldfraktur[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += uppercase_boldfraktur[uppercase_alphabet[letter]]
            elif letter == space:
                returnthis += " "
            else:
                returnthis += letter
    return returnthis


def fancy(string):
    """Convert a string to fancy."""
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += fancy_lowercase[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += fancy_uppercase[uppercase_alphabet[letter]]
            elif letter == space:
                returnthis += " "
            else:
                returnthis += letter
    return returnthis


def bold_fancy(string):
    """Convert a string to bold fancy."""
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += bold_fancy_lowercase[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += bold_fancy_uppercase[uppercase_alphabet[letter]]
            elif letter == space:
                returnthis += " "
            else:
                returnthis += letter
    return returnthis


def smallcaps(string):
    """Convert a string to small caps."""
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += smallcaps_alphabet[alphabet[letter]]
            else:
                returnthis += letter
    return returnthis


def ball_response():
    """8 Ball response randomizer"""
    returnthis = random.choice(eight_ball_responses)
    return returnthis


def uwuize_string(string: str):
    """Uwuize and return a string."""
    converted = ""
    current_word = ""
    for letter in string:
        if letter.isprintable() and not letter.isspace():
            current_word += letter
        elif current_word:
            converted += uwuize_word(current_word) + letter
            current_word = ""
        else:
            converted += letter
    if current_word:
        converted += uwuize_word(current_word)
    return converted


def uwuize_word(word: str):
    """Uwuize and return a word.
    Thank you to the following for inspiration:
    https://github.com/senguyen1011/UwUinator
    """
    word = word.lower()
    uwu = word.rstrip(".?!,")
    punctuations = word[len(uwu) :]
    final_punctuation = punctuations[-1] if punctuations else ""
    extra_punctuation = punctuations[:-1] if punctuations else ""

    # Process punctuation
    if final_punctuation == "." and not random.randint(0, 3):
        final_punctuation = random.choice(KAOMOJI_JOY)
    if final_punctuation == "?" and not random.randint(0, 2):
        final_punctuation = random.choice(KAOMOJI_CONFUSE)
    if final_punctuation == "!" and not random.randint(0, 2):
        final_punctuation = random.choice(KAOMOJI_JOY)
    if final_punctuation == "," and not random.randint(0, 3):
        final_punctuation = random.choice(KAOMOJI_EMBARRASSED)
    if final_punctuation and not random.randint(0, 4):
        final_punctuation = random.choice(KAOMOJI_SPARKLES)

    # Full word exceptions
    if uwu in ("you're", "youre"):
        uwu = "ur"
    elif uwu == "fuck":
        uwu = "fwickk"
    elif uwu == "shit":
        uwu = "poopoo"
    elif uwu == "bitch":
        uwu = "meanie"
    elif uwu == "asshole":
        uwu = "b-butthole"
    elif uwu in ("dick", "penis"):
        uwu = "peenie"
    elif uwu in ("cum", "semen"):
        uwu = "cummies"
    elif uwu == "ass":
        uwu = "boi pussy"
    elif uwu in ("dad", "father"):
        uwu = "daddy"
    # Normal word conversion
    else:
        # Protect specific word endings from changes
        protected = ""
        if (
            uwu.endswith("le")
            or uwu.endswith("ll")
            or uwu.endswith("er")
            or uwu.endswith("re")
        ):
            protected = uwu[-2:]
            uwu = uwu[:-2]
        elif (
            uwu.endswith("les")
            or uwu.endswith("lls")
            or uwu.endswith("ers")
            or uwu.endswith("res")
        ):
            protected = uwu[-3:]
            uwu = uwu[:-3]
        # l -> w, r -> w, n<vowel> -> ny<vowel>, ove -> uv
        uwu = (
            uwu.replace("l", "w")
            .replace("r", "w")
            .replace("na", "nya")
            .replace("ne", "nye")
            .replace("ni", "nyi")
            .replace("no", "nyo")
            .replace("nu", "nyu")
            .replace("ove", "uv")
            + protected
        )

    # Add back punctuations
    uwu += extra_punctuation + final_punctuation

    # Add occasional stutter
    if (
        len(uwu) > 2
        and uwu[0].isalpha()
        and "-" not in uwu
        and not random.randint(0, 6)
    ):
        uwu = f"{uwu[0]}-{uwu}"

    return uwu


def lmgtfy(url):
    """Return a formatted lmgtfy url."""
    returnthis = f"https://lmgtfy.app/?q={urllib.parse.quote_plus(url)}"
    return returnthis


def balls(ctx):
    """Return a random 8 Ball result."""
    returnthis = f":8ball: | {ball_response()}, **{ctx.author.display_name}**"
    return returnthis


def flipcoin():
    """Return a random coin flip result."""
    returnthis = random.choice(("Heads", "Tails"))
    return returnthis
