FROM python:latest

# install ffmpeg for audio streams
RUN apt update && apt upgrade -y && apt install ffmpeg

# we want stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# add the path to pythonpath
ENV PYTHONPATH "${PYTHONPATH}:/app"

# update pip
RUN python -m pip install --upgrade pip

# install uvloop for faster asyncio
RUN pip install uvloop

# install the requirements
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy over the source files
COPY ./ /app/

# start the bot
WORKDIR /app
CMD ["python", "main.py"]
