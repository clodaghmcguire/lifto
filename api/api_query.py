import requests
import json
import pprint as pp


def get_liftover(build: str, variant: str):
    url = f"http://127.0.0.1:5000/api/v1/get_liftover/snv/{build}/{variant}"
    response = requests.get(url)
    return response.json()


def approve_liftover(variant_id: str, confirmation: bool, comments: str, user: str):
    """
    :param variant_id: _id for variant record, obtained from get_liftover query
    :param confirmation: Boolean
    :param comments: String
    :param user: String
    """
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2Nzc3NzMxNDcsInN1YiI6InZhc2EifQ.dv2NqnLqhOkJ6d4Q30lllazTU-JlcRMAWvvnAzspkE0' # update with token from database
    url = f"http://127.0.0.1:5000/api/v1/confirm_liftover/snv/{variant_id}/"
    confirm = {'confirm': confirmation,
               'comments': comments,
               'user': user}
    response = requests.post(url, json=confirm, headers={'x-access-token': token})
    print(response)
    return response.json()


if __name__ == '__main__':
    variant = input("enter variant to query [default: X:48649545:G:A]: ")
    build = input("enter genome build [default: GRCh37]: ")
    liftover = get_liftover(build, variant)
    print(json.dumps(liftover, indent=4))
    confirmation = input("confirm liftover? [True/False]: ")
    if confirmation.lower() == "true":
        confirmation = True
    elif confirmation.lower() == "false":
        confirmation = False
    comments = input("add comments: ")
    user = input("your name: ")
    pp.pprint(approve_liftover(liftover['data']['_id'], confirmation, comments, user))
