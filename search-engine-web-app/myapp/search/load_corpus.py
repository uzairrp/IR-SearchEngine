import json
from typing import List
import pandas as pd

from datetime import datetime   
from myapp.core.utils import load_json_file
from myapp.search.objects import Document


_corpus = {}


# Helper function to extract hashtags
def extract_hashtags(content):
    if not content:
        return []
    return [word for word in content.split() if word.startswith("#")]

def remove_hashtags_from_content(content, hashtags):
    """
    Remove hashtags from the content.
    
    """
    if not content or not hashtags:
        return content
    for hashtag in hashtags:
        content = content.replace(hashtag, "").strip()
    return content


def load_corpus(path):
    """
    Load a corpus from a JSON file where each line is a separate JSON object.

    """
    records = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                item = json.loads(line.strip())  # Parse each JSON object
                record_id = item.get("id")
                if record_id:  # Ensure the ID is present

                    content = item.get("renderedContent", "")
                    hashtags = extract_hashtags(content)
                    clean_content = remove_hashtags_from_content(content, hashtags)


                    records[record_id] = {
                        "id": record_id,
                        "title": content.split("\n")[0],
                        "content": clean_content,
                        "date": datetime.fromisoformat(item.get("date")).date(),
                        "likes": item.get("likeCount", 0),
                        "retweets": item.get("retweetCount", 0),
                        "url": item.get("url"),
                        "hashtags": extract_hashtags(item.get("content", "")),
                    }
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON line: {line}\n{e}")
    
    return records

def get(record_id: str):
    return _corpus.get(record_id)




