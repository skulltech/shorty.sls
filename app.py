import json
import os
import random
import re
import string
from decimal import Decimal

import boto3
from flask import Flask, jsonify, request, redirect, abort

app = Flask(__name__)
URLS_TABLE = os.environ['URLS_TABLE']
IS_OFFLINE = os.environ.get('IS_OFFLINE')

if IS_OFFLINE:
    db = boto3.resource(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
    )
else:
    db = boto3.resource('dynamodb')
table = db.Table(URLS_TABLE)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return int(o)
        return super(DecimalEncoder, self).default(o)


app.json_encoder = DecimalEncoder


@app.route('/<string:slug>')
def shorty(slug):
    inspect = False
    if slug[-1] == '+':
        slug = slug[:-1]
        inspect = True

    response = table.get_item(Key={'slug': slug})
    item = response.get('Item')
    if not item:
        abort(404)
    long_url = item.get('longUrl')

    if inspect:
        return long_url

    response = table.update_item(
        Key={'slug': slug},
        UpdateExpression='ADD visits :inc',
        ExpressionAttributeValues={':inc': 1}
    )
    return redirect(long_url if '://' in long_url else 'http://' + long_url, code=301)


@app.route('/api/urls/<string:slug>')
def get_url(slug):
    response = table.get_item(Key={'slug': slug})
    item = response.get('Item')
    if not item:
        return jsonify({'error': 'URL does not exist'}), 404

    return jsonify(item)


@app.route('/api/urls', methods=['POST'])
def create_url():
    slug = request.json.get('slug')
    long_url = request.json.get('longUrl')
    if not long_url:
        return jsonify({'error': 'Please provide longUrl'}), 400
    if not slug:
        slug = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    elif not re.match('^[a-z0-9._-]{1,16}$', slug):
        return jsonify({'error': 'Invalid slug, must contain only lowercase letters, hyphen, dot and underscore'}), 400

    try:
        response = table.put_item(
            ConditionExpression='attribute_not_exists(slug)',
            Item={
                'slug': slug,
                'longUrl': long_url,
                'visits': 0
            })
    except db.meta.client.exceptions.ConditionalCheckFailedException as e:
        return jsonify({'error': 'slug already exists'}), 400

    return jsonify({
        'slug': slug,
        'longUrl': long_url,
        'visits': 0
    })
