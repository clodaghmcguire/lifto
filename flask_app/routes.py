from flask import Blueprint, jsonify
import datetime
from cmmodule.utils import read_chain_file
from cmmodule.mapvcf import crossmap_vcf_file
from .liftolib import variant_format_valid, assembly_valid, write_vcf

bp = Blueprint('auth', __name__, url_prefix='')


@bp.route('/', methods=['GET'])
def home():
  return "<h1>SEGLH Lift Over API</h1>\
      <p>See <a href='https://git.kingspm.uk/SEGLH/lifto/src/branch/develop'>\
      https://git.kingspm.uk/SEGLH/lifto/src/branch/develop</a> for more info.</p>"


@bp.route('/api/v1/<input_assembly>/<input_variant>', methods=(['GET']))
def api(input_assembly, input_variant):

  if not variant_format_valid(input_variant):
    result = {
      "result": "FAILED",
      "error": "Invalid input variant formatting: {}".format(input_variant)
      }
    output_assembly = 'n/a'

  elif not assembly_valid(input_assembly):
    result = {
      "result": "FAILED",
      "error": "Invalid assembly: {}".format(input_assembly)
      }
    output_assembly = 'n/a'
  else:
    output_assembly, chain_file, refgenome = assembly_valid(input_assembly)

    write_vcf(input_variant)

    try:
      mapTree, targetChromSizes, sourceChromSizes = read_chain_file(chain_file)
      crossmap_vcf_file(mapping = mapTree, infile="temp/in_file.vcf", outfile="temp/out_file.vcf", liftoverfile=chain_file, refgenome=refgenome)
    except Exception as e:
      result = {
        "result": "FAILED",
        "error": "CROSSMAP ERROR: {}".format(e)
        }
    else:
      ouput = open("temp/out_file.vcf", "r")
      variants = [line.strip() for line in ouput.readlines() if not line.startswith('#')]
      if len(variants) == 1:
        variant = variants[0].split("\t")
        variant = (variant[0].strip('chr') + ":" + variant[1] + ":" + variant[3] + ":" + variant[4])
        result = {
          "result": "MAPPED",
          "target": variant
          }
      elif len(variants) == 0:
        ouput = open("temp/out_file.vcf.unmap", 'r')
        variants = [line.strip() for line in ouput.readlines() if not line.startswith('#')]
        variant = variants[0].split("\t")
        crossmap_error = variant[8]
        variant = (variant[0].strip('chr') + ":" + variant[1] + ":" + variant[3] + ":" + variant[4])
        result = {
        "result": crossmap_error,
        "target": variant
        }
      else:
        result = {
          "result": "UNMAPPED",
          "target": "unknown error"
          }

  output_json = jsonify({
    'data': {
      'input_assembly': input_assembly,
      'input_variant': input_variant,
      'output_assembly': output_assembly,
      'response': result,
      'datetime': datetime.datetime.now()
      }
    })

  return output_json
