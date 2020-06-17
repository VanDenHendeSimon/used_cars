from bs4 import BeautifulSoup as bs
import requests
import os


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
    print(data_layer)
    print(car_info)

    return {}


def main():
    print(get_listing_details('https://www.2dehands.be/a/auto-s/mercedes-benz/m1522593070-mercedes-benz-gle-250-d-4-matic-amg-vl-top-conditie-4-pneus.html'))
    return 'ok'

    initial_data = get_json(
        'https://www.2dehands.be/lrp/api/search?attributeRanges[]=constructionYear%3A2000%3Anull&attributesById[]=10882&l1CategoryId=91&limit=100&offset=0&viewOptions=gallery-view'
    )

    if "exception" not in initial_data.keys():
        if not initial_data['hasErrors']:
            listings = {
                'result_count': initial_data['totalResultCount']
            }

            for listing in initial_data['listings']:
                # print_listing(listing)

                img_url = ''
                for img in listing['imageUrls']:
                    # replacing by 86 makes the image high res
                    img_url = "https:%s" % img.replace("$_82", "$_86")
                    download_image(img_url, os.path.join(os.path.curdir, '%s.jpeg' % listing['itemId']))

                mileage = -1
                construction_year = -1
                carpass_url = ''
                for attribute in listing['attributes']:
                    if attribute['key'] == 'carPassUrl':
                        carpass_url = attribute['value']
                    elif attribute['key'] == 'mileage':
                        mileage = attribute['value']
                    elif attribute['key'] == 'constructionYear':
                        construction_year = attribute['value']

                listings[listing['itemId']] = {
                    'title': listing['title'],
                    'city': listing['location']['cityName'],
                    'country': listing['location']['countryName'],
                    'description': listing['description'],
                    'price': int(listing['priceInfo']['priceCents']) * 0.01,
                    'mileage': int(mileage),
                    'construction_year': int(construction_year),
                    'carpass_url': carpass_url,
                    'details_url': "https://www.2dehands.be%s" % listing['vipUrl'],
                    'image_url': img_url
                }

                listings.update(get_listing_details(listings[listing['itemId']]['details_url']))
                break

            print(listings)


if __name__ == '__main__':
    main()
