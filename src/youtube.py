from googleapiclient.discovery import build
from config import config
from datetime import datetime
from pathlib import Path
from dateutil import parser
import os
import re

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey=config["API_KEY"])

def validate_live_stream_id(input_string):
    """
    Extracts video ID from YouTube URL or returns the string as is if it's already an ID.

    Supported formats:
    - https://www.youtube.com/watch?v=uvubgYqg9VQ
    - https://www.youtube.com/live/uvubgYqg9VQ?si=dfmI1IOGu4NRlxtM
    - https://youtu.be/uvubgYqg9VQ
    - uvubgYqg9VQ (direct ID)

    Args:
        input_string (str): YouTube video URL or ID

    Returns:
        str: Extracted video ID or None if extraction failed
    """
    if not input_string:
        return None

    # Patterns for different YouTube URL formats
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtube\.com/live/)([a-zA-Z0-9_-]{11})',  # watch?v= or live/
        r'youtu\.be/([a-zA-Z0-9_-]{11})',  # youtu.be/
        r'^([a-zA-Z0-9_-]{11})$'  # Direct ID (11 characters)
    ]

    for pattern in patterns:
        match = re.search(pattern, input_string)
        if match:
            return match.group(1)

    # If nothing found, return None
    print(f"Failed to extract ID from string: {input_string}")
    return None

# This consumes a lot of quota (100 units per call)
def get_live_streams(channel_id):
    """Retrieve all currently live streams for a given channel with their titles"""
    request = youtube.search().list(
        part="id,snippet",  # Include snippet to get titles
        channelId=channel_id,
        eventType="live",  # Only get currently live videos
        type="video"
    )
    response = request.execute()

    live_streams = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        live_streams.append({"video_id": video_id, "title": title})

    return live_streams

def get_live_stream(livestream_id):
    """Retrieve a single live stream by its ID"""
    request = youtube.videos().list(
        part="snippet",
        id=livestream_id
    )
    response = request.execute()

    if response.get("items"):
        return response["items"][0]
    else:
        return None

def get_live_chat_id(live_stream_id):
    response = youtube.videos().list(
        part="liveStreamingDetails",
        id=live_stream_id
    ).execute()

    return response["items"][0]["liveStreamingDetails"]["activeLiveChatId"]

def get_live_chat_messages(live_chat_id):
    response = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part="snippet,authorDetails"
    ).execute()

    for item in response["items"]:
        author = item["authorDetails"]["displayName"]
        message = item["snippet"]["displayMessage"]
        print(f"{author}: {message}")


# Global set to track seen message IDs
seen_messages = set()
def get_new_live_chat_messages(live_chat_id):
    """Fetch and print only new chat messages (including super chats and super stickers) that haven't been printed before."""
    response = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part="snippet,authorDetails"
    ).execute()

    # Define log directory
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists

    # Generate log file path
    log_file = log_dir / f"chat_{datetime.today().strftime('%Y-%m-%d')}.txt"

    messages = []
    log_lines = []
    for item in response["items"]:
        message_id = item["id"]  # Unique message ID
        if message_id not in seen_messages:
            seen_messages.add(message_id)  # Mark as seen

            author = item["authorDetails"]["displayName"]
            message = item["snippet"]["displayMessage"]
            timestamp = parser.parse(item["snippet"]["publishedAt"]).strftime("%Y-%m-%d %H:%M:%S")

            # Check for super chat first, then for super sticker
            if "superChatDetails" in item["snippet"]:
                sc_details = item["snippet"]["superChatDetails"]
                amount = sc_details.get("amountDisplayString", "N/A")
                log_message = f"[{timestamp}] Super Chat from {author} ({amount}): {message}"
            elif "superStickerDetails" in item["snippet"]:
                ss_details = item["snippet"]["superStickerDetails"]
                amount = ss_details.get("amountDisplayString", "N/A")
                tier = ss_details.get("tier", "N/A")
                log_message = f"[{timestamp}] Super Sticker from {author} (Tier {tier}, {amount}): {message}"
            else:
                log_message = f"[{timestamp}] {author}: {message}"

            log_lines.append(log_message)

            messages.append({
                "timestamp": timestamp,
                "author": author,
                "message": message,
                "sc_details": item["snippet"].get("superChatDetails", None),
                "ss_details": item["snippet"].get("superStickerDetails", None)
            })

    if log_lines:
        with open(log_file, "a+", encoding="utf-8") as chat_file:
            chat_file.write("\n".join(log_lines) + "\n")

    return messages

def get_subscriber_count(channel_id):
    """Get the subscriber count for a given channel ID."""
    request = youtube.channels().list(
        part="statistics",
        id=channel_id
    )
    response = request.execute()

    if response["items"]:
        return int(response["items"][0]["statistics"]["subscriberCount"])
    else:
        return None
