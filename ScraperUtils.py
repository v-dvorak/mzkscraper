import requests


def get_json_from_url(url: str):
    """
    Given an url string, returns a JSON object.

    :param url: url string

    :returns: JSON object or None, if the request fails
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
            return json_data
        else:
            print(f"Error: Failed to retrieve data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
