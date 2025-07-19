#!/usr/bin/env python3
"""
Test functions validate_live_stream_id
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the function (you need to temporarily comment out the API initialization in youtube.py for testing)
import re

def validate_live_stream_id(input_string):
    """
    Extracts the video ID from a YouTube URL or returns the string as-is if it's already an ID.
    """
    if not input_string:
        return None
    
    # Patterns for various YouTube URL formats
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtube\.com/live/)([a-zA-Z0-9_-]{11})',  # watch?v= or live/
        r'youtu\.be/([a-zA-Z0-9_-]{11})',  # youtu.be/
        r'^([a-zA-Z0-9_-]{11})$'  # Direct ID (11 characters)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, input_string)
        if match:
            return match.group(1)
    
    return None

# Test cases
test_cases = [
    "https://www.youtube.com/watch?v=uvubgYqg9VQ",
    "https://www.youtube.com/live/uvubgYqg9VQ?si=dfmI1IOGu4NRlxtM", 
    "https://youtu.be/uvubgYqg9VQ",
    "uvubgYqg9VQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s",
    "invalid_url",
    ""
]

print("Function testing validate_live_stream_id:")
print("=" * 50)

for test_url in test_cases:
    result = validate_live_stream_id(test_url)
    print(f"Input: {test_url}")
    print(f"Result: {result}")
    print("-" * 30)
