

all: GRCh38ToGRCh37.chain GRCh37ToGRCh38.chain grch38.dict grch37.dict

# get chainfile for hg19 to GRCh37 (basically just chromosome name mapping)
hg19ToGRCh37.over.chain:
	wget -c https://raw.githubusercontent.com/liguowang/CrossMap/v0.3.2/data/UCSC_chain/hg19ToGRCh37.over.chain.gz
	gunzip hg19ToGRCh37.over.chain

# get chainfiles from UCSC
hg19ToHg38.over.chain:
	wget -c http://hgdownload.soe.ucsc.edu/goldenPath/hg19/liftOver/hg19ToHg38.over.chain.gz
	gunzip hg19ToHg38.over.chain.gz

hg38ToHg19.over.chain:
	wget -c http://hgdownload.soe.ucsc.edu/goldenPath/hg38/liftOver/hg38ToHg19.over.chain.gz
	gunzip hg38ToHg19.over.chain.gz

# GRCh37 uses the RCS MT sequence as GRCh38,
# must patch the 1-to-1 mapping into the UCSC chainfiles
GRCh37_to_GRCh38.chain.gz:
	wget -c ftp://ftp.ensembl.org/pub/assembly_mapping/homo_sapiens/GRCh37_to_GRCh38.chain.gz

GRCh38ToGRCh37.rcspatch.chain: GRCh37_to_GRCh38.chain.gz
	gunzip -c GRCh37_to_GRCh38.chain.gz | \
		awk '{ if (/^$$/) { out=0 } else if ($$3=="MT") { out=1; $$3="chrM"; $$8="MT"; print } else if (out==1) { print } }' > \
		GRCh38ToGRCh37.rcspatch.chain

GRCh37ToGRCh38.rcspatch.chain: GRCh37_to_GRCh38.chain.gz
	gunzip -c GRCh37_to_GRCh38.chain.gz | \
		awk '{ if (/^$$/) { out=0 } else if ($$3=="MT") { out=1; $$3="MT"; $$8="chrM"; print } else if (out==1) { print } }' > \
		GRCh37ToGRCh38.rcspatch.chain

# we use GRCh37 so we need to substitute chromosome names of hg19 with GRCh37 names
# remove the chrM mapping to be replaced by 1to1 mapping as GRCh37 and GRCh38 both use RCS sequence
GRCh38ToGRCh37.chain: hg38ToHg19.over.chain hg19ToGRCh37.over.chain GRCh38ToGRCh37.rcspatch.chain
	awk '{ if (NR==FNR) { chrom[$$3]=$$8 } else { if (/chain/ && chrom[$$8]) { $$8=chrom[$$8] } print }}' \
		hg19ToGRCh37.over.chain hg38ToHg19.over.chain | \
		awk '{ if (/^$$/) { rem=0; print } else if (/chrM/ || rem==1) { rem=1 } else { rem=0; print } }' | \
		awk '{ if (/^$$/) { empty+=1; if (empty==1) { print } } else { empty=0; print } }' | \
		cat - GRCh38ToGRCh37.rcspatch.chain > GRCh38ToGRCh37.chain

GRCh37ToGRCh38.chain: hg19ToHg38.over.chain hg19ToGRCh37.over.chain GRCh37ToGRCh38.rcspatch.chain
	awk '{ if (NR==FNR) { chrom[$$3]=$$8 } else { if (/chain/ && chrom[$$3]) { $$3=chrom[$$3] } print }}' \
		hg19ToGRCh37.over.chain hg19ToHg38.over.chain | \
		awk '{ if (/^$$/) { rem=0; print } else if (/chrM/ || rem==1) { rem=1 } else { rem=0; print } }' | \
		awk '{ if (/^$$/) { empty+=1; if (empty==1) { print } } else { empty=0; print } }' | \
		cat - GRCh37ToGRCh38.rcspatch.chain > GRCh37ToGRCh38.chain

# get references
grch37.fa:
	wget -c -O grch37.fa.gz ftp://ftp-trace.ncbi.nih.gov/1000genomes/ftp/technical/reference/phase2_reference_assembly_sequence/hs37d5.fa.gz
	gunzip grch37.fa.gz

grch38.fa:
	wget -c -O grch38.fa.gz ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.15_GRCh38/seqs_for_alignment_pipelines.ucsc_ids/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna.gz
	gunzip grch38.fa.gz

grch37.dict: grch37.fa
	java -jar ../bin/picard.jar CreateSequenceDictionary -R grch37.fa

grch38.dict: grch38.fa
	java -jar ../bin/picard.jar CreateSequenceDictionary -R grch38.fa