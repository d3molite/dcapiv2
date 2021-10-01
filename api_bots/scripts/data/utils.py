def clean_vue(data):
    """method to turn an array of vue dicts into a single dict"""
    cleaned = {}

    for field in data:
        cleaned[field["key"]] = field["data"]

    return cleaned
