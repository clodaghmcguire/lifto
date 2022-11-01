import requests
import json
import pprint as pp


def get_liftover(build, variant):
    url = f"http://127.0.0.1:5000/api/v1/snv/{build}/{variant}"
    response = requests.get(url)
    return response.json()


def approve_liftover(variant_id, confirmation, comments, user):
    url = f"http://127.0.0.1:5000/api/v1/{variant_id}/"
    confirm = {'confirm': confirmation,
               'comments': comments,
               'user': user}
    response = requests.get(url, json=confirm)
    print(response)
    return response.json()


if __name__ == '__main__':
    variant = input("enter variant to query [default: X:48649545:G:A]: ")
    build = input("enter genome build [default: GRCh37]: ")
    liftover = get_liftover(build, variant)
    print(json.dumps(liftover, indent=4))
    confirm_lifto = input("confirm liftover? [True/False]: ")
    if confirm_lifto.lower() == "true":
        confirmation = True
    else:
        confirmation = False
    comments = input("add comments: ")
    user = input("your name: ")
    pp.pprint(approve_liftover(liftover['data']['_id']['$oid'], confirmation, comments, user))
