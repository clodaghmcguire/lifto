import re
import os
import requests
import jsonschema
from jsonschema import validate
import jwt
from functools import wraps
from flask import request, make_response, jsonify, current_app
from .db import tokens


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        # ensure the jwt-token is passed with the headers
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token: # throw error if no token provided
            return make_response(jsonify({"message": "A valid token is missing!"}), 401)
        saved_token = tokens.find_one({'token': token})
        if saved_token:
            try:
               # decode the token to obtain user public_id
                current_user = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            except Exception as e:
                print(e)
                return make_response(jsonify({"message": "Invalid token!"}), 401)
        else:
            print("token not stored in db")
            return make_response(jsonify({"message": "Invalid token!"}), 401)
         # Return the user information attached to the token
        return f(current_user, *args, **kwargs)
    return decorator


def snv_format_valid(snv_variant: str) -> bool:
    pattern = re.compile(r"^[0-9XYMT]{1,2}:\d+:[ACGTacgt]+:[ACGTacgt]+$")
    if pattern.match(snv_variant):
        return True
    else:
        return False


def sv_format_valid(sv_input: str) -> bool:
    pattern = re.compile(r"^[0-9XYMT]{1,2}:\d+:\d+$")
    if pattern.match(sv_input):
        return True
    else:
        return False


def assembly_valid(input_assembly: str) -> bool:
    if input_assembly.lower() in ['grch37', 'grch38']:
        return True
    else:
        return False


def normalise_assembly(input_assembly: str) -> str:
    if input_assembly.lower() == 'grch37':
        return 'GRCh37'
    elif input_assembly.lower() == 'grch38':
        return 'GRCh38'
    else:
        raise Exception(f"Invalid assembly {input_assembly}")


def get_chain_files(input_assembly: str) -> dict:
    if input_assembly.lower() == 'grch37':
        return {
            'output_assembly': 'GRCh38',
            'chain_file': '/resources/GRCh37ToGRCh38.chain',
            'refgenome': '/resources/grch38.fa'
            }
    elif input_assembly.lower() == 'grch38':
        return {
            'output_assembly': 'GRCh37',
            'chain_file': '/resources/GRCh38ToGRCh37.chain',
            'refgenome': '/resources/grch37.fa'
            }
    else:
        raise Exception(f"No chain files found for {input_assembly}")


def write_vcf(input_variant: str) -> str:
    output_file = 'in_file.vcf'
    if os.path.exists(output_file):
        os.remove(output_file)

    CHROM, POS, REF, ALT = input_variant.split(":")
    with open(output_file, 'w') as writer:
        writer.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
        writer.write(f"{CHROM}\t{POS}\t.\t{REF}\t{ALT}\t.\t.\t.\n")
    return output_file


def valid_vcf(f: str) -> bool:
    with open(f, "r") as data:
        variant_entries = [line.strip() for line in data.readlines() if not line.startswith('#')]
        if len(variant_entries) == 1:
            return True
        else:
            return False


def read_vcf(f: str, mapped_vcf: bool) -> str:
    with open(f, "r") as data:
        variant_entries = [line.strip() for line in data.readlines() if not line.startswith('#')]
        variant = variant_entries[0].split("\t")
        variant_string = f"{variant[0].strip('chr')}:{variant[1]}:{variant[3]}:{variant[4]}"
        if mapped_vcf:
            return variant_string
        else:
            crossmap_error = variant[8]
            return f"{variant_string}: {crossmap_error}"


def write_bed(input_variant: str) -> str:
    output_file = 'in_file.bed'
    if os.path.exists(output_file):
        os.remove(output_file)

    CHROM, START, END = input_variant.split(":")
    with open(output_file, 'w') as writer:
        writer.write(f"{CHROM}\t{START}\t{END}")
    return output_file


def valid_bed(f: str) -> bool:
    with open(f, "r") as data:
        line = [line.strip() for line in data.readlines() if not line.startswith('#')]
        if len(line) == 1:
            return True
        else:
            return False


def read_bed(f: str, mapped_bed: bool) -> str:
    with open(f, "r") as data:
        line = [line.strip() for line in data.readlines() if not line.startswith('#')]
        sv = line[0].split("\t")
        sv_string = f"{sv[0].strip('chr')}:{sv[1]}:{sv[2]}"
        if mapped_bed:
            return sv_string
        else:
            crossmap_error = sv[3]
            return f"{sv_string}: {crossmap_error}"


def annotate(assembly: str, variant: str):
    url = f"https://rest.variantvalidator.org/VariantValidator/variantvalidator/{normalise_assembly(assembly)}/{variant}/all?content-type=application%2Fjson"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


liftoSchema = {
    "type": "object",
    "properties": {
        "confirm": {"type": "boolean"},
        "user": {"type": "string"},
        "comments": {"type": "string"}
    }
}


def validateJson(data) -> bool:
    try:
        validate(instance=data, schema=liftoSchema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True
