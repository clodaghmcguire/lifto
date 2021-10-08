# lifto

A picard based liftover service

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

