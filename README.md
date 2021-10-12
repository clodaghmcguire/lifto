# lifto

Uses the UCSU liftover executable from https://genome-store.ucsc.edu/
Build docker container with make file:
- Downloads liftover tool
- Downloads chain files and makes conversion from hg19 to GRCh37
- Builds docker container - currently gets tagged as kingspm/lifto:0.1 (not in dockerhub at present)
- Removes all downloaded files after build

Simple query at: http://server/api/v1/<input_assembly>/<input_variant>
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

## Capabilities

- translate coordinates (variant) to a different assembly version
- return information about mapping (one-to-one, reciprocal, collapsed, spread...)
- Ability to curate a variant liftover by accepting or rejecting (user, timestamp, decision)


## API 

liftO provides a RESTful API to translate single variants and batches of variants between assemblies

### Endpoints

1. GET - /chain - get all available chains

2. POST - /lift/{source}/{target}/ - lift list of variants of format (chr:pos:ref:alt)

3. POST - /lift/{source}/{target}/ - lift list of variants of format (chr:pos:ref:alt)

4. GET - /result/{id}/ - get result by hash 

## Process

1. write variants to VCF
2. Run Picard
3. Parse results
4. Parse fails
5. Build response
6. Save result

## Data Models

### source

sourceid
assembly
chrom
pos
ref
alt

### mapping

sourceid
targetid

### target
targetid
assembly
chrom
pos
ref
alt


### Response
```
[
  {
    source: {
      assembly: "grch37",
      chrom: "1",
      pos: 123,
      ref: "A",
      alt: "N"
    },
    targets: [
      {
        assembly: "grch37",
        chrom: "1",
        pos: 123,
        ref: "A",
        alt: "N"
      },
      {
        assembly: "grch37",
        chrom: "1",
        pos: 123,
        ref: "A",
        alt: "N"
      }
    ],
    quality: {
      uniq: false, # uniquely maps to other asssembly
      runiq: false  # reciprocal unique mapping
    }
  }
]
```
## Resources

- JAVA
- Picard binary
- reference file
- chain file

