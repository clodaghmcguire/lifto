from flask import Blueprint, jsonify, request
import datetime
import os
import json
from bson import json_util
from bson.objectid import ObjectId
from pymongo import MongoClient
from cmmodule.utils import read_chain_file
from cmmodule.mapvcf import crossmap_vcf_file
from cmmodule.mapbed import crossmap_bed_file
from .functions import snv_format_valid, sv_format_valid, assembly_valid, write_vcf, write_bed, read_vcf, read_bed, \
    annotate, validateJson
bp = Blueprint('auth', __name__, url_prefix='')
client = MongoClient('localhost', 27017)
db = client.flask_db
lifto = db.lifto


@bp.route('/', methods=['GET'])
def home():
    return "<h1>SEGLH Lift Over API</h1>\
      <p>See <a href='https://git.kingspm.uk/SEGLH/lifto/src/branch/develop'>\
      https://git.kingspm.uk/SEGLH/lifto/src/branch/develop</a> for more info.</p>"


@bp.route('/api/v1/snv/<input_assembly>/<snv_variant>', methods=(['GET']))
def snv_liftover(input_assembly, snv_variant):

    if not snv_format_valid(snv_variant):
        output = {
            "query": {"assembly": input_assembly, "variant": snv_variant},
            "mapping": "FAILED",
            "warning": "Invalid input variant formatting: {}".format(snv_variant),
            "datetime": datetime.datetime.now()
        }
        output_json = jsonify({"data": output})

    elif not assembly_valid(input_assembly):
        output = {
            "query": {"assembly": input_assembly, "variant": snv_variant},
            "mapping": "FAILED",
            "warning": "Invalid assembly: {}".format(input_assembly),
            "datetime": datetime.datetime.now()
        }
        output_json = jsonify({"data": output})
    else:
        input_CHROM, input_POS, input_REF, input_ALT = snv_variant.split(":")

        existing_variant = lifto.find_one({
            "query.assembly": input_assembly, "query.chrom": input_CHROM, "query.pos": input_POS,
            "query.ref": input_REF, "query.alt": input_ALT
        })
        if existing_variant:
            output = json.loads(json_util.dumps(existing_variant))
            output_json = jsonify({"data": output})

        else:
            output_assembly, chain_file, refgenome = assembly_valid(input_assembly)

            write_vcf(snv_variant)

            try:
                outfile = "out_file.vcf"
                if os.path.exists(outfile):
                    os.remove(outfile)

                mapTree, targetChromSizes, sourceChromSizes = read_chain_file(chain_file)
                crossmap_vcf_file(
                    mapping=mapTree, infile="in_file.vcf",
                    outfile=outfile, liftoverfile=chain_file, refgenome=refgenome
                )
            except Exception as e:
                output = {"query": {
                    "assembly": input_assembly,
                    "chrom": input_CHROM,
                    "pos": input_POS,
                    "ref": input_REF,
                    "alt": input_ALT
                },
                    "evidence": [{
                        "mapping": "FAILED",
                        "actor": "lifto",
                        "datetime": datetime.datetime.now(),
                        "meta": {"warning": "CROSSMAP ERROR: {}".format(e)}
                    }],
                    "meta": {
                        "datetime": datetime.datetime.now()
                    }

                }
                submit_query = lifto.insert_one(output)
                output_json = jsonify({"data": json.loads(json_util.dumps(output))})
                return output_json

            mapped_variant = read_vcf(outfile, mapped_vcf=True)
            if mapped_variant:
                CHROM, POS, REF, ALT = mapped_variant.split(":")

                annotation = annotate(input_assembly, snv_variant)


                try:
                    #transcript = next(iter(annotation))
                    #vv_liftover = annotation[transcript]['primary_assembly_loci'][output_assembly.lower()]['vcf']
                    vv_liftover = [v for k, v in annotation.items() if 'primary_assembly_loci' in v][0]['primary_assembly_loci'][output_assembly.lower()]['vcf']
                    vv_mapping = {
                        "assembly": output_assembly,
                        "chrom": vv_liftover['chr'],
                        "pos": vv_liftover['pos'],
                        "ref": vv_liftover['ref'],
                        "alt": vv_liftover['alt'],
                    }
                except:
                    vv_mapping = "no mapping provided"

                output = {
                    "query": {
                        "assembly": input_assembly,
                        "chrom": input_CHROM,
                        "pos": input_POS,
                        "ref": input_REF,
                        "alt": input_ALT
                    },
                    "evidence": [
                        {"mapping": {
                            "assembly": output_assembly,
                            "chrom": CHROM,
                            "pos": POS,
                            "ref": REF,
                            "alt": ALT,
                        },
                            "actor": "lifto",
                            "datetime": datetime.datetime.now(),
                            "meta": {}
                        },
                        {"mapping": vv_mapping,
                         "actor": "VariantValidator",
                         "datetime": datetime.datetime.now(),
                         "meta": {
                             "variantvalidator": annotation
                         }

                         }],
                    "meta": {
                        "datetime": datetime.datetime.now()
                    }
                }

                submit_query = lifto.insert_one(output)
                output_json = jsonify({"data": json.loads(json_util.dumps(output))})

            else:
                unmapped_variant, crossmap_error = read_vcf("{}.unmap".format(outfile), mapped_vcf=False)
                output = {"query": {
                    "assembly": input_assembly,
                    "chrom": input_CHROM,
                    "pos": input_POS,
                    "ref": input_REF,
                    "alt": input_ALT
                },
                    "evidence": [{
                        "mapping": "FAILED",
                        "actor": "lifto",
                        "datetime": datetime.datetime.now(),
                        "meta": {
                            "warning": "MAPPING ERROR: {} {}".format(unmapped_variant, crossmap_error)}}],
                    "meta": {
                        "datetime": datetime.datetime.now()
                    }
                }

                submit_query = lifto.insert_one(output)
                output_json = jsonify({"data": json.loads(json_util.dumps(output))})
    return output_json


@bp.route('/api/v1/<variant>/', methods=(['GET', 'POST']))
def confirm_liftover(variant):
    verification_data = request.get_json(silent=True)
    isValid = validateJson(verification_data)
    if isValid:
        existing_variant = lifto.find_one({"_id": ObjectId(variant)})
        update_record = lifto.update_one({"_id": ObjectId(variant)},
                                         {"$push": {
                                             "evidence":
                                                 {"mapping": existing_variant['evidence'][0]['mapping'],
                                                  "confirm": verification_data['confirm'],
                                                  "actor": verification_data['user'],
                                                  "datetime": datetime.datetime.now(),
                                                  "meta": {"comments": verification_data['comments']}
                                                  }
                                         }})
        existing_variant = lifto.find_one({"_id": ObjectId(variant)})
        output_json = jsonify(json.loads(json_util.dumps(existing_variant)))

    else:
        output = {"verification": verification_data,
                  "warning": "data provided in incorrect format, check jsonschema"}
        output_json = jsonify({"data": json.loads(json_util.dumps(output))})
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
            outfile = "out_file.bed"
            if os.path.exists(outfile):
                os.remove(outfile)
            mapTree, targetChromSizes, sourceChromSizes = read_chain_file(chain_file)
            crossmap_bed_file(mapping=mapTree, inbed="in_file.bed", outfile=outfile)
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
