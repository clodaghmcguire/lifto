from flask import Blueprint, jsonify, request, Response
import datetime
import os
import json
import uuid
from bson import json_util
from cmmodule.utils import read_chain_file
from cmmodule.mapvcf import crossmap_vcf_file
from cmmodule.mapbed import crossmap_bed_file
from .functions import snv_format_valid, sv_format_valid, assembly_valid, normalise_assembly, get_chain_files, \
    write_vcf, write_bed, valid_vcf, read_vcf, valid_bed, read_bed, annotate, validateJson, token_required
from .db import lifto

bp = Blueprint('auth', __name__, url_prefix='')

@bp.route('/', methods=['GET'])
def home():
    return "<h1>SEGLH Lift Over API</h1>\
            <p>See <a href='https://git.kingspm.uk/SEGLH/lifto/'>https://git.kingspm.uk/SEGLH/lifto</a> for more info.</p>"


@bp.route('/api/v1/get_liftover/snv/<input_assembly>/<snv_variant>', methods=(['GET']))
def snv_liftover(input_assembly, snv_variant):

    if not snv_format_valid(snv_variant):
        output = {
            "query": {"assembly": input_assembly, "variant": snv_variant},
            'evidence': [{
                "mapping": "FAILED",
                "actor": "lifto",
                "meta": {
                    "warning": f"Invalid input variant formatting: {snv_variant}"
                }
            }]
        }
        output_json = json.dumps({"data": output})
        return Response(
            output_json,
            status=400,
        )

    elif not assembly_valid(input_assembly):
        output = {
            "query": {"assembly": input_assembly, "variant": snv_variant},
            "evidence": [{
                "mapping": "FAILED",
                "actor": "lifto",
                "meta": {
                    "warning": f"Invalid assembly: {input_assembly}"
                }
            }]
        }
        output_json = json.dumps({"data": output})
        return Response(
            output_json,
            status=400,
        )

    else:
        input_CHROM, input_POS, input_REF, input_ALT = snv_variant.split(":")
        input_assembly = normalise_assembly(input_assembly)

        existing_variant = lifto.find_one({
            "query.assembly": input_assembly, "query.chrom": input_CHROM, "query.pos": input_POS,
            "query.ref": input_REF, "query.alt": input_ALT
        })
        if existing_variant:
            output = json.loads(json_util.dumps(existing_variant))

        else:
            liftover_files = get_chain_files(input_assembly)
            write_vcf(snv_variant)

            try:
                outfile = "out_file.vcf"
                if os.path.exists(outfile):
                    os.remove(outfile)

                mapTree, targetChromSizes, sourceChromSizes = read_chain_file(liftover_files['chain_file'])
                crossmap_vcf_file(
                    mapping=mapTree, infile="in_file.vcf",
                    outfile=outfile, liftoverfile=liftover_files['chain_file'], refgenome=liftover_files['refgenome']
                )
            except Exception as e:
                output = {
                    "query": {
                    "assembly": input_assembly,
                    "chrom": input_CHROM,
                    "pos": input_POS,
                    "ref": input_REF,
                    "alt": input_ALT
                },
                    "evidence": [{
                        "mapping": "FAILED",
                        "actor": "lifto",
                        "datetime": datetime.datetime.now().isoformat(),
                        "meta": {"warning": f"CROSSMAP ERROR: {e}"}
                    }]
                }
                output_json = jsonify({"data": output})
                return output_json

            if valid_vcf(outfile):
                mapped_variant = read_vcf(outfile, mapped_vcf=True)
                CHROM, POS, REF, ALT = mapped_variant.split(":")

                output = {"_id": str(uuid.uuid4()),
                    "query": {
                        "assembly": input_assembly,
                        "chrom": input_CHROM,
                        "pos": input_POS,
                        "ref": input_REF,
                        "alt": input_ALT
                    },
                    "evidence": [
                        {"mapping": {
                            "assembly": liftover_files['output_assembly'],
                            "chrom": CHROM,
                            "pos": POS,
                            "ref": REF,
                            "alt": ALT,
                        },
                            "actor": "lifto",
                            "datetime": datetime.datetime.now().isoformat(),
                            "meta": {}
                        }
                        ],
                    "record_created": datetime.datetime.now().isoformat(),
                    "record_modified": datetime.datetime.now().isoformat()
                }

                annotation = annotate(input_assembly, snv_variant)

                if annotation:
                    try:
                        vv_liftover = \
                        [v for k, v in annotation.items() if 'primary_assembly_loci' in v][0]['primary_assembly_loci'][
                            liftover_files['output_assembly'].lower()]['vcf']
                        vv_mapping = {
                            "assembly": liftover_files['output_assembly'],
                            "chrom": vv_liftover['chr'],
                            "pos": vv_liftover['pos'],
                            "ref": vv_liftover['ref'],
                            "alt": vv_liftover['alt'],
                        }
                    except Exception as e:
                        vv_mapping = f"no mapping provided: {e}"
                    vv_annotation = {"mapping": vv_mapping,
                         "actor": "VariantValidator",
                         "datetime": datetime.datetime.now().isoformat(),
                         "meta": {
                             "variantvalidator": annotation
                         }
                         }
                    output['evidence'].append(vv_annotation)
                    output['record_modified'] = datetime.datetime.now().isoformat()
                lifto.insert_one(output)

            else:
                crossmap_error = read_vcf(f"{outfile}.unmap", mapped_vcf=False)
                output = {"_id": str(uuid.uuid4()),
                    "query": {
                    "assembly": input_assembly,
                    "chrom": input_CHROM,
                    "pos": input_POS,
                    "ref": input_REF,
                    "alt": input_ALT
                },
                    "evidence": [{
                        "mapping": "FAILED",
                        "actor": "lifto",
                        "datetime": datetime.datetime.now().isoformat(),
                        "meta": {
                            "warning": f"MAPPING ERROR: {crossmap_error}"
                        }
                    }],
                    "record_created": datetime.datetime.now().isoformat(),
                    "record_modified": datetime.datetime.now().isoformat()
                }

                lifto.insert_one(output)  # cached failed liftover for checking problem regions later
    output_json = jsonify({"data": output})
    return output_json


@bp.route('/api/v1/confirm_liftover/snv/<variant>/', methods=(['GET', 'POST']))
@token_required
def confirm_liftover(token, variant):
    verification_data = request.get_json(silent=True)
    if validateJson(verification_data):
        existing_variant = lifto.find_one({"_id": variant})
        lifto.update_one(
            {"_id": variant},
            {
                "$push": {
                    "evidence":
                        {"mapping": existing_variant['evidence'][0]['mapping'],
                        "confirm": verification_data['confirm'],
                        "actor": token['sub'],
                        "datetime": datetime.datetime.now().isoformat(),
                        "meta": {"user": verification_data['user'],
                                 "comments": verification_data['comments']}
                         }
                },
                "$set": {
                    "record_modified": datetime.datetime.now().isoformat()
                }}
            )
        updated_variant = lifto.find_one({"_id": variant})
        output_json = jsonify({"data": json.loads(json_util.dumps(updated_variant))})

    else:
        output = {"verification": verification_data,
                  "warning": "data provided in incorrect format, check jsonschema"}
        output_json = jsonify({"data": json.loads(json_util.dumps(output))})
    return output_json


@bp.route('/api/v1/get_failed_liftover/', methods=(['GET']))
def get_failed_liftover():
    variants = lifto.find({"evidence.mapping": "FAILED"})
    output_json = jsonify({"data": json.loads(json_util.dumps(variants))})
    return output_json


# @bp.route('/api/v1/get_liftover/sv/<input_assembly>/<sv_input>', methods=(['GET']))
# def sv_liftover(input_assembly, sv_input):
#
#     if not sv_format_valid(sv_input):
#         result = {
#             "result": "FAILED",
#             "output": f"Invalid input sv formatting: {sv_input}"
#         }
#
#     elif not assembly_valid(input_assembly):
#         result = {
#             "result": "FAILED",
#             "output": f"Invalid assembly: {input_assembly}"
#         }
#     else:
#         liftover_files = get_chain_files(input_assembly)
#         write_bed(sv_input)
#
#         try:
#             outfile = "out_file.bed"
#             if os.path.exists(outfile):
#                 os.remove(outfile)
#             mapTree, targetChromSizes, sourceChromSizes = read_chain_file(liftover_files['chain_file'])
#             crossmap_bed_file(mapping=mapTree, inbed="in_file.bed", outfile=outfile)
#         except Exception as e:
#             result = {
#                 "result": "FAILED",
#                 "output": f"CROSSMAP ERROR: {e}"
#             }
#         else:
#             if valid_bed(outfile):
#                 mapped_sv = read_bed(outfile, mapped_bed=True)
#                 result = {
#                     "result": "MAPPED",
#                     'output_assembly': liftover_files['output_assembly'],
#                     "output": mapped_sv
#                 }
#             else:
#                 crossmap_error = read_bed(f"{outfile}.unmap", mapped_bed=False)
#                 result = {
#                     "result": "FAILED",
#                     "output": f"MAPPING ERROR: {crossmap_error}"
#                 }
#
#     output_json = jsonify({
#         'data': {
#             'input_assembly': input_assembly,
#             'input_variant': sv_input,
#             'response': result,
#             'datetime': datetime.datetime.now().isoformat()
#         }
#     })
#
#     return output_json
