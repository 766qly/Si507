import json
import requests
def write_json(filepath, data, encoding='utf-8', ensure_ascii=False, indent=2):
    """Serializes object as JSON. Writes content to the provided filepath.

    Parameters:
        filepath (str): the path to the file
        data (dict)/(list): the data to be encoded as JSON and written to the file
        encoding (str): name of encoding used to encode the file
        ensure_ascii (str): if False non-ASCII characters are printed as is;
                            otherwise non-ASCII characters are escaped.
        indent (int): number of "pretty printed" indention spaces applied to encoded JSON

    Returns:
        None
    """

    with open(filepath, 'w', encoding=encoding) as file_obj:
        json.dump(data, file_obj, ensure_ascii=ensure_ascii, indent=indent)

def read_json(filepath, encoding='utf-8'):
    """Reads a JSON file and converts it to a Python dictionary.

    Parameters:
        filepath (str): a path to the JSON file
        encoding (str): name of encoding used to decode the file

    Returns:
        dict/list: dict or list representations of the decoded JSON document
    """
    with open(filepath, 'r', encoding=encoding) as file_obj:
        return json.load(file_obj)



api_key = 'RNADtfAbkrCrsBI27-GYnbDysNYjR4Ixft73SjQjEMTwlG6u4BNqiUgR5TPvf4vxnGwQ1WMdX7wocEO9-_M6P68ejiDZa4eQ45nzwQkllrzXQm6uodhfMrTbo_NCY3Yx'
headers = {'Authorization': 'Bearer %s' % api_key}

base_url = 'https://api.yelp.com/v3/businesses/search'

class Place:
    def __init__(self, id="", name="No Name", url="No URL", location={}, categories="No Categories", transactions="", price=None, rating="", phone="", is_closed=True, json=None):
        self.id = json['id']
        self.name = json['name']
        self.url = json['url']
        self.location = json['location']
        self.categories = json['categories']
        self.transactions = json['transactions']
        if 'price' in json:
            self.price = json['price']
        else:
            self.price = price
        self.rating = json['rating']
        self.phone = json['phone']
        self.is_closed = json['is_closed']

    def info(self):
        if self.location['address2'] and self.location['address3']:
            return f'{self.name}\nphone: {self.phone}\naddress: {self.location["address1"]} {self.location["address2"]} {self.location["address3"]} \nrating: {self.rating} \nprice: {self.price}\n'
        if self.location['address2']:
            return f'{self.name}\nphone: {self.phone}\naddress: {self.location["address1"]} {self.location["address2"]} \nrating: {self.rating} \nprice: {self.price}\n'
        return f'{self.name}\nphone: {self.phone}\naddress: {self.location["address1"]} \nrating: {self.rating} \nprice: {self.price}\n'

class Review:
    def __init__(self, user={}, text="", time_created="", url='', rating='', json=None):
        self.user = json['user']
        self.text = json['text']
        self.time = json['time_created']
        self.url = json['url']
        self.rating = json['rating']
    
    def info(self):
        print(f'time: {self.time}')
        print(f'rating: {self.rating}')
        print(f'text: {self.text}')

class TreeNode:
    def __init__(self, children=None, business=None, ):
        self.children = children
        self.business = business


def retireve_data_by_term_location(term_name, location, num_obj=20, headers=headers):
    parameter_dictionary = {'term': term_name,'location': location, 'limit': num_obj}
    response = requests.get(base_url, params=parameter_dictionary, headers=headers)
    write_json('test2.json', data=response.json())
    res = json.loads(response.text)
    return res

def find_reviews(id, headers=headers):
    review_url = f'https://api.yelp.com/v3/businesses/{id}/reviews'
    response = requests.get(review_url, headers=headers)
    res = json.loads(response.text)
    return res

def store_in_tree(place, root):
    if not place.price:
        return
    price = place.price
    city = place.location['city']
    price_node = root.children[price]
    

    city_node = None
    if city in price_node.children.keys():
        city_node = price_node.children[city]
    else:
        city_node = TreeNode(children={})
        price_node.children[city] = city_node
    
    if place.id not in city_node.children.keys():
        city_node.children[f'{place.id}'] = place

def give_recommendation(root, price, city):
    price_node = root.children[price]
    city_node = price_node.children[city]
    i = 0
    for _, place in city_node.children.items():
        print(place.info())
        i += 1
        if i == 20:
            break


def load_cahce(filename):
    try:
        data = read_json(filename)
    except:
        data = None
    return data


def create_cache_tree(data, root):
    for business in data:
        store_in_tree(Place(json=business), root)
    return root




if __name__ == "__main__":
    data = load_cahce('test3.json')
    root = TreeNode(children={})
    price_degree = '$'
    for i in range(4):
        child = TreeNode(children={})
        root.children[price_degree] = child
        price_degree += '$'

    if not data:
        data = []

    for business in data:
        store_in_tree(Place(json=business), root)

    try:
        dict_exist = read_json('test4.json')
    except:
        dict_exist = {}


    while True:
        option = input("Please choose what to do search or recommendation? ")
        if option == 'search':
            term = input("Please first enter the term you want to search. ")
            location = input("Please enter the loaction that you want to do search. ")
            if f'{term.lower()} {location.lower()}' in dict_exist.keys():
                results = dict_exist[f'{term.lower()} {location.lower()}']
            else:
                results = retireve_data_by_term_location(term, location)['businesses']
                dict_exist[f'{term.lower()} {location.lower()}'] = results
                data.extend(results)
                for business in results:
                    store_in_tree(Place(json=business), root)

            print("Here is the list of searched results:")

            for i in range(len(results)):
                temp = Place(json=results[i])
                print(f'{i + 1}' + " " + temp.info())
            #TODO review

        elif option == 'recommendation':
            #TODO recommendation
            pass
        else:
            print("The input is invalid please try again! ")
            continue

        option2 = input("Do you want to do another search?(y/n) ")
        if option2 == 'y':
            continue
        else:
            write_json('test3.json', data)
            write_json('test4.json', dict_exist)
            print("Bye")
            break





    # data = retireve_data_by_term_location('seafood', 'New York City')
    # res1 = Place(json=data['businesses'][0])
    # # review = find_reviews(res1.id)
    # # review1 = Review(json=review['reviews'][0])
    # # review1.info()

    # root = TreeNode(children={})
    # price_degree = '$'
    # for i in range(4):
    #     child = TreeNode(children={})
    #     root.children[price_degree] = child
    #     price_degree += '$'
    # #store_in_tree(res1, root)
    # for business in data['businesses']:
    #     store_in_tree(Place(json=business), root)

    # give_recommendation(root, '$$', 'New York')


