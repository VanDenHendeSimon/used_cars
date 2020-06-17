from models.DataRepository import DataRepository

from bs4 import BeautifulSoup as bs
import requests
import time
import os
import re


def download_image(url, filename):
    if not os.path.exists(filename):
        response = requests.get(url).content

        with open(filename, 'wb') as f:
            f.write(response)

    else:
        print("%s already exists" % filename)


def get_text(url):
    return requests.get(url).text


def get_json(url):
    try:
        return requests.get(url).json()
    except Exception as ex:
        return {"exception": ex}


def print_listing(listing):
    for k, v in listing.items():
        print("%s: %s" % (k, v))

    print("\n---\n")


def get_between_chars(text, start_char, end_char):
    pattern = "\%s(.*?)\%s" % (start_char, end_char)
    return re.findall(pattern, text)[0].replace('\\u0020', ' ')


def get_listing_details(listing_details_url):
    details = get_text(listing_details_url)
    soup = bs(details, 'html.parser')
    scripts = soup.find_all('script')
    scripts = [
        str(link).strip() for link in scripts
        if 'src' not in link.attrs and
           'type' not in link.attrs
    ]

    data_layer = scripts[0]
    car_info = next(str(script).strip().replace('\n', '') for script in scripts if 'car:' in script)

    # Focus op motorinhoud, brandstof, transmissie, adverteerder
    data_layer = data_layer[data_layer.find("\"attr\"")+9:]
    data_layer = data_layer[:data_layer.find("}")]

    details_dict = dict()
    for idx, line in enumerate(data_layer.split('\n')):
        try:
            key = get_between_chars(line.split(":")[0], '"', '"')
            value = get_between_chars(line.split(":")[1], '"', '"')

            details_dict[key] = value

        except IndexError:
            continue

    car_info = car_info[car_info.find('car:')+8:]
    car_info = car_info[:car_info.find('}')]
    car_info = [info.strip() for info in car_info.split(',')]

    for info in car_info:
        key = info.split(":")[0]
        value = get_between_chars(info, "'", "'")

        details_dict[key] = value

    if 'Carrosserie' not in details_dict.keys():
        details_dict['Carrosserie'] = None

    if 'Euronorm' not in details_dict.keys():
        details_dict['Euronorm'] = None

    if 'Motorinhoud' not in details_dict.keys():
        details_dict['Motorinhoud'] = None

    if 'Transmissie' not in details_dict.keys():
        details_dict['Transmissie'] = None

    if 'Adverteerder' not in details_dict.keys():
        details_dict['Adverteerder'] = None

    return details_dict


def main():
    initial_data = get_json(
        'https://www.2dehands.be/lrp/api/search?attributeRanges[]=constructionYear%3A2000%3Anull&attributesById[]=10882&l1CategoryId=91&limit=100&offset=0&viewOptions=gallery-view'
    )

    if "exception" not in initial_data.keys():
        if not initial_data['hasErrors']:
            for listing in initial_data['listings']:
                # print_listing(listing)

                img_url = ''
                for img in listing['imageUrls']:
                    # replacing by 86 makes the image high res
                    img_url = "https:%s" % img.replace("$_82", "$_86")
                    # download_image(img_url, os.path.join(os.path.curdir, '%s.jpeg' % listing['itemId']))

                mileage = None
                construction_year = None
                carpass_url = None
                for attribute in listing['attributes']:
                    if attribute['key'] == 'carPassUrl':
                        carpass_url = attribute['value']
                    elif attribute['key'] == 'mileage':
                        mileage = attribute['value']
                    elif attribute['key'] == 'constructionYear':
                        construction_year = attribute['value']

                listing_details = get_listing_details("https://www.2dehands.be%s" % listing['vipUrl'])
                time.sleep(0.05)

                if 'description' not in listing.keys():
                    listing['description'] = None

                try:
                    DataRepository.create_listing(
                        _id=listing['itemId'],
                        titel=listing['title'],
                        beschrijving=listing['description'],
                        stad=listing['location']['cityName'],
                        prijs=int(listing['priceInfo']['priceCents']) * 0.01,
                        km_stand=int(mileage),
                        bouwjaar=int(construction_year),
                        carpass_url=carpass_url,
                        details_url="https://www.2dehands.be%s" % listing['vipUrl'],
                        image_url=img_url,
                        transmissie=listing_details['Transmissie'],
                        adverteerder=listing_details['Adverteerder'],
                        brandstof=listing_details['Brandstof'],
                        merk=listing_details['make'],
                        model=listing_details['model'],
                        euronorm=listing_details['Euronorm'],
                        motor_inhoud=listing_details['Motorinhoud'],
                        carrosserie=listing_details['Carrosserie'],
                    )

                except Exception as ex:
                    print("Error: %s" % ex)
                    print(listing_details)
                    print('\n')
                    continue


if __name__ == '__main__':
    main()
