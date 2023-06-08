# lifto

Uses Python Crossmap library from https://crossmap.readthedocs.io/

### SNV Liftover Endpoint
Simple query at: http://[server]/api/v1/get_liftover/snv/[input_assembly]/[input_variant]

eg: http://localhost:5000/api/v1/get_liftover/snv/grch37/11:5247992:C:A"


#### Output:

```
{
  "data": {
    "_id": "538cda30-88dd-4d3f-ba4b-cad1bf0c2b03", 
    "query": {
      "assembly": "GRCh37", 
      "chrom": "11", 
      "pos": "5247992", 
      "ref": "C", 
      "alt": "A"
    }, 
    "evidence": [
      {
        "mapping": {
          "assembly": "GRCh38", 
          "chrom": "11", 
          "pos": "5226762", 
          "ref": "C", 
          "alt": "A"
        }, 
        "actor": "lifto", 
        "datetime": "2023-02-17", 
        "meta": {}
      }
    ],
    "record_created": "2023-03-02T15:31:42.417468", 
    "record_modified": "2023-03-02T15:31:43.918932"
  }
}
```

### Confirm SNV Liftover endpoint
Confirm or contest a liftover by making a post request to http://[server]/api/v1/confirm_liftover/snv/[variant_id]
Variant_id is the '_id' for the variant record, obtained from the SNV Liftover endpoint.
Authorization token required.
Confirmation data should include a confirmation, username and comments provided in json format. Example query provided in api/api_query.py

### Get failed liftover endpoint
Retrieve a list of all variants that have failed to map between genome builds. 
Simple query at: http://[server]/api/v1/get_failed_liftover/

#### Output
```
{
  "data": [
    {
      "_id": "58afca5d-5dd0-45bd-9ec9-32ab7e491839", 
      "query": {
        "assembly": "GRCh37", 
        "chrom": "9", 
        "pos": "43625193", 
        "ref": "TG", 
        "alt": "T"
      }, 
      "evidence": [
        {
          "mapping": "FAILED", 
          "actor": "lifto", 
          "datetime": "2023-03-02T12:02:16.341146", 
          "meta": {
            "warning": "MAPPING ERROR: 9:43625193:TG:T: Fail(Unmap)"
          }
        }
      ], 
      "record_created": "2023-03-02T12:02:16.341172", 
      "record_modified": "2023-03-02T12:02:16.341176"
    }, 
    {
      "_id": "13469f2a-0f47-4824-b630-275426c244b3", 
      "query": {
        "assembly": "GRCh37", 
        "chrom": "19", 
        "pos": "40408526", 
        "ref": "CTCCCCGGCGGG", 
        "alt": "C"
      }, 
      "evidence": [
        {
          "mapping": "FAILED", 
          "actor": "lifto", 
          "datetime": "2023-03-02T14:46:31.102177", 
          "meta": {
            "warning": "MAPPING ERROR: 19:40408526:CTCCCCGGCGGG:C: Fail(Unmap)"
          }
        }
      ], 
      "record_created": "2023-03-02T14:46:31.102191", 
      "record_modified": "2023-03-02T14:46:31.102195"
    }
  ]
}
```
## Install/run

Use the makefile to generate reference files:
- Downloads chain files and makes conversion from hg19 to GRCh37
- Downloads GRCh37/38 reference sequences
- Copied to local 'resources' folder (requires volume mapping in Docker compose file)

Use the docker-compose to run the dockerised container, or the Dockerfile to build your own image


Create development Mongo database
```commandline
mkdir mongo_data
chmod 777 -R mongo_data
sudo docker-compose -f docker-compose-dev.yml up -d
```

Run flask in virtual environment

Check path to resources folder in get_chain_files() in flask_app/functions.py points to correct location and update if needed
```commandline
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=flask_app
export SECRET_KEY="Th1s1sAS3cr3t"
export FLASK_DEBUG=1
flask run
```