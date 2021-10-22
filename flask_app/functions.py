import re


def variant_format_valid(input_variant):
  pattern = re.compile("^[0-9XYMT]{1,2}:\d+:[ACGTacgt]+:[ACGTacgt]+$")
  if pattern.match(input_variant):
    return True
  else:
    return False


def assembly_valid(input_assembly):
  if input_assembly.lower() in ['grch37','37']:
    return 'GRCh38', '/resources/GRCh37ToGRCh38.chain', '/resources/grch38.fa'
  elif input_assembly.lower() in ['grch38','38']:
    return 'GRCh37', '/resources/GRCh38ToGRCh37.chain', '/resources/grch37.fa'
  else:
    return False


def write_vcf(input_variant):
  output_file='in_file.vcf'
  CHROM, POS, REF, ALT = input_variant.split(":")
  with open(output_file, 'w') as writer:
    writer.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
    writer.write(CHROM + "\t" + POS + "\t.\t" + REF + "\t" + ALT + "\t.\t.\t.\n")
  return output_file

  
def read_vcf(f, mapped_vcf=True):
  data = open(f, "r")
  variant_entries = [line.strip() for line in data.readlines() if not line.startswith('#')]
  if len(variant_entries) == 1:
    variant = variant_entries[0].split("\t")
    variant_string = (variant[0].strip('chr') + ":" + variant[1] + ":" + variant[3] + ":" + variant[4])
    if mapped_vcf:
      return variant_string
    else:
      crossmap_error = variant[8]
      return variant_string, crossmap_error
  else:
    return False


