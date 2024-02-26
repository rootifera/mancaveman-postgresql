import requests


def get_book_info(isbn, api_key=None):
    base_url = "https://www.googleapis.com/books/v1/volumes"

    params = {"q": f"isbn:{isbn}"}

    if api_key:
        params["key"] = api_key

    try:
        response = requests.get(base_url, params=params)

        if response.status_code == 400:
            error_message = "Bad Request: Invalid API Key"
            return {"error": error_message}
        elif response.status_code == 429:
            error_message = "Too many requests"
            return {"error": error_message}

        response.raise_for_status()
        book_data = response.json()

        if "items" in book_data:
            this_book = {}
            volume_info = book_data["items"][0]["volumeInfo"]

            this_book.update({'title': volume_info.get('title', '')})
            this_book.update({'subtitle': volume_info.get('subtitle', '')})
            this_book.update({'author': volume_info.get('authors', [''])[0]})  # temporary
            this_book.update({'publisher': volume_info.get('publisher', '')})
            this_book.update({'published_date': volume_info.get('publishedDate', '')})
            this_book.update({'description': volume_info.get('description', '')})
            this_book.update({'category': volume_info.get('categories', [''])[0]})  # temporary
            this_book.update({'print_type': volume_info.get('printType', '')})
            this_book.update({'maturity_rating': volume_info.get('maturityRating', '')})

            identifiers = volume_info.get('industryIdentifiers', [])
            this_book.update({'isbn_10': identifiers[1]['identifier'] if len(identifiers) > 1 else ''})
            this_book.update({'isbn_13': identifiers[0]['identifier'] if identifiers else ''})

            return this_book
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None
