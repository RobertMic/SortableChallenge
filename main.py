#Code written by Robert Mic for the sortable coding challenge at http://sortable.com/challenge/

import json
import argparse
from collections import defaultdict

encoding_standard = 'utf-8'

def main():
    args = handle_args()
    #files must be opened with utf8 encoding so a UnicodeDecodingError is avoided
    try:
        matcher = Matcher(open(args.products_file, 'r+', encoding = encoding_standard), open(args.listings_file,'r+', encoding = encoding_standard))
    except FileNotFoundError:
        print("One (or both) of the files was not found")

    output = matcher.process()
    with open('./output/results.txt', 'w', encoding = encoding_standard) as output_file:
        for key in output:
            new_line = json.dumps({"product_name": key, "listings":output[key]}, ensure_ascii = False )
            output_file.write(new_line + '\n')


class Matcher:
    def __init__(self, products_file, listings_file):
        self._get_products(products_file)
        self._get_listings(listings_file)

    #Will do the actual work of trying to match a product for each listing
    #It will then return a dictonary that maps a product name to an array of listings
    def process(self):
        ret = defaultdict(list)

        for line in self.listings:
            current_listing = json.loads(line)
            normalized_title = self._normalize(current_listing['title'])
            found,product = self._contains(normalized_title, current_listing['manufacturer'])
            #if we found a match, we can add it to the return dict
            if found is True:
                ret[product['product_name']].append(current_listing)

        return ret

    def _get_products(self, file):
        #make a dictionary that maps a string to an array of json strings
        #this will map manufacturers to their products so not all items are checked per listing
        self.products = defaultdict(list)
        
        for line in file:
            next_line = json.loads(line)
            self.products[next_line['manufacturer']].append(next_line)

    def _get_listings(self,file):
        self.listings = file

    #removes all spaces, '-' and makes everything lower case and returns the new string
    def _normalize(self, string):
        ret = string.replace(' ', '')
        ret = ret.replace('-', '')
        return ret.lower()

    #takes a normalized listing and checks agains all products to see if one matches
    #if one does match it return true, and the product
    #else false,None
    #NOTE: listing_manufacturer should not be normalized, as both files already follow the same standard
    #well for the most part atleast, some places stick ' Canada' at the end, this handles that
    def _contains(self, listing_title, listing_manufacturer):
        to_look = self.products[listing_manufacturer.replace(' Canada', '')]
        best_match = {'score' : -1, 'product' : None}
        
        #find the highest scoring product out of the filtered list
        for product in to_look:
            current_score = self._score(listing_title, self._normalize(product['model']))
            if current_score > best_match['score']:
                best_match['score'] = current_score
                best_match['product'] = product

        return best_match['score'] > -1, best_match['product']

    #'scores' how well the product_model matches a substring of listing_title
    #NOTE: the product_model str is expected to be normalized
    #can later be changed to use other algorithm to get a better estimate
    #right now the score is the amount of characters that matched if the string was found, 0 otherwise
    def _score(self, listing_title, product_model):
        if product_model in listing_title:
            return len(product_model)
        return 0


def handle_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('products_file', type = str)
    parser.add_argument('listings_file', type = str)
    return parser.parse_args()


if __name__ == '__main__':
    main()