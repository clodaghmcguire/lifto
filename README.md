# lifto

Uses Python Crossmap library from https://crossmap.readthedocs.io/

Simple query at: http://[server]/api/v1/[input_assembly]/[input_variant]

eg: http://localhost:5000/api/v1/grch37/1:55516888:A:T

returns:

```
{
  "data": {
    "datetime": "Tue, 12 Oct 2021 15:14:07 GMT", 
    "input_assembly": "grch37", 
    "input_variant": "1:55516888:A:T", 
    "output_assembly": "GRCh38", 
    "result": "1:55051215:A:T"
  }
}
```

## Install/run

Use the makefile to generate reference files:
- Downloads chain files and makes conversion from hg19 to GRCh37
- Downloads GRCh37/38 reference sequences
- Copied to local 'resources' folder (requires volume mapping in Docker compose file)

Use the docker-compose to run the dockerised container, or the Dockerfile to build your own image