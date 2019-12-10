import requests
import json
import logging
import getopt
import sys
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

page_count = 5


def main():
    logger.info('Starting process')

    user = None
    tag = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:t:", ["help", "user=", "tag="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            sys.exit()
        elif o in ("-u", "--user"):
            user = a
        elif o in ("-t", "--tag"):
            tag = a
        else:
            assert False, "unhandled option"

    if user is not None:
        posts = fetch_user_posts(user)
    elif tag is not None:
        posts = fetch_tag_posts(tag)
    else:
        sys.exit(2)

    for item in fetch_locations(posts):
        print(item)


def fetch_user_posts(user):
    result = []
    end_cursor = ''
    for i in range(0, page_count):
        url = 'https://www.instagram.com/{0}/?__a=1&max_id={1}'.format(user, end_cursor)
        print(url)
        r = requests.get(url)
        data = json.loads(r.text)
        for item in (data['graphql']['user']['edge_owner_to_timeline_media']['edges']):
            result.append(item['node']['shortcode'])
        end_cursor = data['graphql']["user"]['edge_owner_to_timeline_media']['page_info']['end_cursor']  # value for the next page
        time.sleep(2)

    return result


def fetch_tag_posts(tag):
    end_cursor = ''
    for i in range(0, page_count):
        url = 'https://www.instagram.com/explore/tags/{0}/?__a=1&max_id={1}'.format(tag, end_cursor)
        r = requests.get(url)
        data = json.loads(r.text)
        end_cursor = data['graphql']['hashtag']['edge_hashtag_to_media']['page_info'][
            'end_cursor']  # value for the next page

    return data['graphql']['hashtag']['edge_hashtag_to_media']['edges']  # list with posts


def fetch_shortcodes(posts):
    arr = []
    for item in posts:
        arr.append(item['node']['shortcode'])

    return arr


def fetch_locations(shortcodes):
    locations = []
    for code in shortcodes:
        url = f'https://www.instagram.com/p/{code}/?__a=1'
        r = requests.get(url)
        data = json.loads(r.text)
        if 'location' in data['graphql']['shortcode_media'] and data['graphql']['shortcode_media'][
            'location'] is not None:
            if data['graphql']['shortcode_media']['location']['address_json'] is not None:
                address = json.loads(data['graphql']['shortcode_media']['location']['address_json'])
                locations.append([data['graphql']['shortcode_media']['location']['name'],
                                  [address['street_address'], address['city_name']]])

    return locations


if __name__ == "__main__":
    main()
