from flask import Flask, jsonify, request, redirect, abort
import os
import boto3
import string
import random
import re

app = Flask(__name__)
URLS_TABLE = os.environ['URLS_TABLE']
IS_OFFLINE = os.environ.get('IS_OFFLINE')

if IS_OFFLINE:
    client = boto3.client(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
        )
else:
    client = boto3.client('dynamodb')


@app.route('/<string:url_id>')
def shorty(url_id):
    response = client.get_item(
        TableName=URLS_TABLE, 
        Key={
            'urlId': {'S': url_id}
        })
    item = response.get('Item')
    if not item:
        abort(404)

    long_url = item.get('longUrl').get('S')
    return redirect(long_url, code=301)


@app.route('/api/urls/<string:url_id>')
def get_url(url_id):
    response = client.get_item(
        TableName=URLS_TABLE, 
        Key={
            'urlId': {'S': url_id}
        })
    item = response.get('Item')
    if not item:
        return jsonify({'error': 'URL does not exist'}), 404
    
    return jsonify({
        'urlId': item.get('urlId').get('S'),
        'longUrl': item.get('longUrl').get('S')
        })


@app.route('/api/urls', methods=['POST'])
def create_url():
    url_id = request.json.get('urlId')
    long_url = request.json.get('longUrl')
    if not long_url:
        return jsonify({'error': 'Please provide longUrl'}), 400
    if not url_id:
        url_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    elif not re.match('^[a-z0-9._-]{1,16}$', url_id):
        return jsonify({'error': 'Invalid urlId, must contain only lowercase letters, hyphen, dot and underscore'}), 400

    response = client.put_item(
        TableName=URLS_TABLE,
        ConditionExpression='attribute_not_exists(url_id)',
        Item={
            'urlId': {'S': url_id},
            'longUrl': {'S': long_url}
        })

    return jsonify({
        'urlId': url_id,
        'longUrl': long_url
        })
