# lifto

Uses Python Crossmap library from https://crossmap.readthedocs.io/

### SNV Liftover Endpoint
Simple query at: http://[server]/api/v1/snv/[input_assembly]/[input_variant]

eg: http://localhost:5000/api/v1/snv/grch37/1:55516888:A:T


### Region (e.g SV) Liftover Endpoint
Simple query at: http://[server]/api/v1/sv/[input_assembly]/[chr]:[start]:[end]

eg: http://localhost:5000/api/v1/sv/grch37/1:55516888:55517999

### Output:

```
{
  "data": {
    "datetime": "Wed, 24 Nov 2021 16:35:22 GMT", 
    "input_assembly": "[grch37|grch38]", 
    "input_variant": "1:55516N888:G:A", 
    "output_assembly": "[grch38|grch37]", 
    "response": {
      "output": "[ Mapped result | Error message ]", 
      "result": "[ MAPPED | FAILED ]"
    }
  }
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
sudo docker-compose up -d
```

Run flask in virtual environment
```commandline
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=flask_app
flask run
```