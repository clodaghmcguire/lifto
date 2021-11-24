from flask import Blueprint, jsonify
import datetime
import os
from cmmodule.utils import read_chain_file
from cmmodule.mapvcf import crossmap_vcf_file
from cmmodule.mapbed import crossmap_bed_file
from .functions import snv_format_valid, sv_format_valid, assembly_valid, write_vcf, write_bed, read_vcf, read_bed

bp = Blueprint('auth', __name__, url_prefix='')


@bp.route('/', methods=['GET'])
def home():
  return "<h1>SEGLH Lift Over API</h1>\
      <p>See <a href='https://git.kingspm.uk/SEGLH/lifto/src/branch/develop'>\
      https://git.kingspm.uk/SEGLH/lifto/src/branch/develop</a> for more info.</p>"


@bp.route('/api/v1/snv/<input_assembly>/<snv_variant>', methods=(['GET']))
def snv_liftover(input_assembly, snv_variant):

  if not snv_format_valid(snv_variant):
    result = {
      "result": "FAILED",
      "output": "Invalid input variant formatting: {}".format(snv_variant)
      }
    output_assembly = 'n/a'

  elif not assembly_valid(input_assembly):
    result = {
      "result": "FAILED",
      "output": "Invalid assembly: {}".format(input_assembly)
      }
    output_assembly = 'n/a'
  else:
    output_assembly, chain_file, refgenome = assembly_valid(input_assembly)

    write_vcf(snv_variant)

    try:
      outfile="out_file.vcf"
      if os.path.exists(outfile):
        os.remove(outfile)

      mapTree, targetChromSizes, sourceChromSizes = read_chain_file(chain_file)
      crossmap_vcf_file(
        mapping = mapTree, infile="in_file.vcf", \
        outfile=outfile, liftoverfile=chain_file, refgenome=refgenome
        )
    except Exception as e:
      result = {
        "result": "FAILED",
        "output": "CROSSMAP ERROR: {}".format(e)
        }
    else:
      mapped_variant = read_vcf(outfile, mapped_vcf=True)
      if mapped_variant:
        result = {
          "result": "MAPPED",
          "output": mapped_variant
          }
      else:
        unmapped_variant, crossmap_error = read_vcf("{}.unmap".format(outfile), mapped_vcf=False)
        result = {
          "result": "FAILED",
          "output": "MAPPING ERROR: {} {}".format(unmapped_variant, crossmap_error)
          }

  output_json = jsonify({
    'data': {
      'input_assembly': input_assembly,
      'input_variant': snv_variant,
      'output_assembly': output_assembly,
      'response': result,
      'datetime': datetime.datetime.now()
      }
    })

  return output_json


@bp.route('/api/v1/sv/<input_assembly>/<sv_input>', methods=(['GET']))
def sv_liftover(input_assembly, sv_input):

  if not sv_format_valid(sv_input):
    result = {
      "result": "FAILED",
      "output": "Invalid input sv formatting: {}".format(sv_input)
      }
    output_assembly = 'n/a'

  elif not assembly_valid(input_assembly):
    result = {
      "result": "FAILED",
      "output": "Invalid assembly: {}".format(input_assembly)
      }
    output_assembly = 'n/a'
  else:
    output_assembly, chain_file, refgenome = assembly_valid(input_assembly)
    write_bed(sv_input)

    try:
      outfile="out_file.bed"
      if os.path.exists(outfile):
        os.remove(outfile)
      mapTree, targetChromSizes, sourceChromSizes = read_chain_file(chain_file)
      crossmap_bed_file(mapping = mapTree, inbed="in_file.bed", outfile=outfile)
    except Exception as e:
      result = {
        "result": "FAILED",
        "output": "CROSSMAP ERROR: {}".format(e)
        }
    else:
      mapped_sv = read_bed(outfile, mapped_bed=True)
      if mapped_sv:
        result = {
          "result": "MAPPED",
          "output": mapped_sv
          }
      else:
        unmapped_variant, crossmap_error = read_bed("{}.unmap".format(outfile), mapped_bed=False)
        result = {
          "result": "FAILED",
          "output": "MAPPING ERROR: {} {}".format(unmapped_variant, crossmap_error)
          }

  output_json = jsonify({
    'data': {
      'input_assembly': input_assembly,
      'input_variant': sv_input,
      'output_assembly': output_assembly,
      'response': result,
      'datetime': datetime.datetime.now()
      }
    })

  return output_json