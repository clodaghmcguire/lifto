import re
import os
import requests

def snv_format_valid(snv_variant):
  pattern = re.compile("^[0-9XYMT]{1,2}:\d+:[ACGTacgt]+:[ACGTacgt]+$")
  if pattern.match(snv_variant):
    return True
  else:
    return False


def sv_format_valid(sv_input):
  pattern = re.compile("^[0-9XYMT]{1,2}:\d+:\d+$")
  if pattern.match(sv_input):
    return True
  else:
    return False


def assembly_valid(input_assembly):
  if input_assembly.lower() in ['grch37','37']:
    return 'GRCh38', 'resources/GRCh37ToGRCh38.chain', 'resources/grch38.fa'
  elif input_assembly.lower() in ['grch38','38']:
    return 'GRCh37', 'resources/GRCh38ToGRCh37.chain', 'resources/grch37.fa'
  else:
    return False


def write_vcf(input_variant):
  output_file='in_file.vcf'
  if os.path.exists(output_file):
    os.remove(output_file)

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


def write_bed(input_variant):
  output_file='in_file.bed'
  if os.path.exists(output_file):
    os.remove(output_file)

  CHROM, START, END = input_variant.split(":")
  with open(output_file, 'w') as writer:
    writer.write(CHROM + "\t" + START + "\t" + END)
  return output_file


def read_bed(f, mapped_bed=True):
  data = open(f, "r")
  line = [line.strip() for line in data.readlines() if not line.startswith('#')]
  if len(line) == 1:
    sv = line[0].split("\t")
    sv_string = (sv[0].strip('chr') + ":" + sv[1] + ":" + sv[2])
    if mapped_bed:
      return sv_string
    else:
      crossmap_error = sv[3]
      return sv_string, crossmap_error
  else:
    return False


def annotate(assembly, variant):
  if assembly.lower() in ['grch37','37']:
    assembly = 'GRCh37'
  elif assembly.lower() in ['grch38','38']:
    assembly = 'GRCh38'
  url = f"https://rest.variantvalidator.org/VariantValidator/variantvalidator/{assembly}/{variant}/mane_select?content-type=application%2Fjson"
  response = requests.get(url)
  return response.json()


def validate(output_assembly, mapped_variant, annotation):
  assembly = output_assembly.lower()
  transcript = next(iter(annotation))
  variant = annotation[transcript]['primary_assembly_loci'][assembly]['vcf']
  variantvalidator_mapping = variant['chr']+':'+variant['pos']+':'+variant['ref']+':'+variant['alt']
  if variantvalidator_mapping == mapped_variant:
    return f"validated mapped variant {mapped_variant}, VariantValidator mapped variant {variantvalidator_mapping}"
  else:
    return f"variant mismatch with mapped variant {mapped_variant} and VariantValidator mapped variant {variantvalidator_mapping}"
