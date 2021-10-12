import os
import re
import datetime
from flask import Blueprint
from flask import jsonify

bp = Blueprint('blueprint', __name__)

@bp.route('/', methods=['GET'])
def home():
    return "<h1>SEGLH Lift Over API</h1><p>See <a href='https://git.kingspm.uk/SEGLH/lifto/src/branch/develop'>https://git.kingspm.uk/SEGLH/lifto/src/branch/develop</a> for more info.</p>"


@bp.route('/api/v1/<input_assembly>/<input_variant>', methods=(['GET']))
def api(input_assembly, input_variant):

  # Variant format check
  pattern = re.compile("^[0-9XMT]{1,2}:\d+:[ACGTacgt]+:[ACGTacgt]+$")
  if not pattern.match(input_variant):
    return jsonify({"ERROR": "Invalid input variant formatting"})

  # Assembly check
  if input_assembly.lower() in ['grch37','37']:
    output_assembly = 'GRCh38'
    chain_file = 'resources/GRCh37ToGRCh38.chain'
  elif input_assembly.lower() == ['grch38','38']:
    output_assembly = 'GRCh38'
    chain_file = 'resources/GRCh38ToGRCh37.chain'
  else:
    return jsonify({"ERROR": "Invalid assembly"})

  # Perform liftover
  CHROM, POS, REF, ALT = input_variant.split(":")
  with open('input.bed', 'w') as writer:
    writer.write(CHROM + "\t" + POS + "\t" + POS + "\n")

  os.system('bin/liftOver input.bed {} mapped.bed unmapped.bed'.format(chain_file))

  ouput = open('mapped.bed', 'r')
  variant = [line.strip() for line in ouput.readlines() if not line.startswith('#')]
  if len(variant) == 1:
    variant = variant[0].split("\t")
    result = variant[0].strip('chr') + ":" + variant[1] + ":" + REF + ":" + ALT
  else:
    ouput = open('unmapped.bed', 'r')
    result = [line.strip() for line in ouput.readlines() if line.startswith('#')][0]

  output_json = jsonify({
    'data': {
      'input_assembly': input_assembly,
      'input_variant': input_variant,
      'output_assembly': output_assembly,
      'result': result,
      'datetime': datetime.datetime.now()
      }
    })

  return output_json


def get_picard_liftover(target_assembly, variant):

  '''
  liftover errors

  Deleted in new:
      Sequence intersects no chains
  Partially deleted in new:
      Sequence insufficiently intersects one chain
  Split in new:
      Sequence insufficiently intersects multiple chains
  Duplicated in new:
      Sequence sufficiently intersects multiple chains
  Boundary problem:
      Missing start or end base in an exon
  '''

  CHROM, POS, REF, ALT = variant.split(":")

  with open('input.vcf', 'w') as writer:
    writer.write('##fileformat=VCFv4.2\n')
    writer.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n')
    writer.write(CHROM + "\t" + POS + "\t.\t" + REF + "\t" + ALT + "\t.\t.\t.\n")

  
  os.system('java -Xmx8g -jar bin/picard.jar LiftoverVcf I=input.vcf O=output.vcf CHAIN=hg19ToHg38.over.chain REJECT=reject.vcf R=hg38.fa')

  ouput = open('output.vcf', 'r')
  variant = [line for line in ouput.readlines() if not line.startswith('#')]
  if len(variant) == 1:
    variant = variant[0].split("\t")
    result = variant[0] + ":" + variant[1] + ":" + variant[3] + ":" + variant[4]
  else:
    ouput = open('reject.vcf', 'r')
    variant = [line for line in ouput.readlines() if not line.startswith('#')]
    variant = variant[0].split("\t")
    result = variant[6]


  print("result is {}".format(result))
