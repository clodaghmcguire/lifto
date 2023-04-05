from flask_app import create_app
import pytest
import json

@pytest.fixture()
def test_data():
    f = open('./tests/test_data.json')
    test_data = json.load(f)
    return test_data


@pytest.fixture()
def client():
    return create_app().test_client()


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200


def test_invalid_build(client):
    response = client.get("/api/v1/get_liftover/snv/grch34/17:7577547:C:A")
    assert response.status_code == 400


def test_invalid_snv(client):
    response = client.get("/api/v1/get_liftover/snv/grch37/17-7577547-C-A")
    assert response.status_code == 400


def test_snv_liftover(client, test_data):
    for record in test_data['variants']:
        response = client.get(f"/api/v1/get_liftover/snv/{record['assembly']}/{record['variant']}")
        assembly = response.json['data']['evidence'][0]['mapping']['assembly']
        chrom = response.json['data']['evidence'][0]['mapping']['chrom']
        pos = response.json['data']['evidence'][0]['mapping']['pos']
        ref = response.json['data']['evidence'][0]['mapping']['ref']
        alt = response.json['data']['evidence'][0]['mapping']['alt']
        assert response.status_code == 200
        assert assembly == record['liftover_assembly']
        assert f"{chrom}:{pos}:{ref}:{alt}" == record['liftover_variant']

def test_failed_list(client):
    response = client.get("/api/v1/get_failed_liftover/")
    assert response.status_code == 200

def test_unauthorised_verification(client):
    response = client.get("/api/v1/get_liftover/snv/grch37/17:7577547:C:A")
    var_id = response.json['data']['_id']
    data = {
        'confirm': True,
         'comments': "Verified",
         'user': "Test_user"
    }
    verify = client.post(f"/api/v1/confirm_liftover/snv/{var_id}/", json=data)
    assert verify.status_code == 401


def test_authorised_verification(client):
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2Nzc3NzMxNDcsInN1YiI6InZhc2EifQ.dv2NqnLqhOkJ6d4Q30lllazTU-JlcRMAWvvnAzspkE0' #update with valid token
    response = client.get("/api/v1/get_liftover/snv/grch37/17:7577547:C:A")
    var_id = response.json['data']['_id']
    data = {
        'confirm': True,
        'comments': "Verified",
        'user': "Test_user"
    }
    verify = client.post(f"/api/v1/confirm_liftover/snv/{var_id}/", json=data, headers={'x-access-token': token})
    assert verify.status_code == 200
