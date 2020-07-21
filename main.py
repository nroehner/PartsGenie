'''
PartsGenie (c) GeneGenie Bioinformatics Ltd. 2020

All rights reserved.

@author:  neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=no-member
# pylint: disable=wrong-import-order
import json
import os
import sys
import tempfile
import traceback
import uuid
import zipfile

from Bio import Restriction
from flask import Flask, jsonify, request, Response
from werkzeug.utils import secure_filename

from genegeniebio.utils import ice_utils, net_utils, uniprot_utils
from ice import export
import manager
import organisms
# from codon_genie import codon_utils
# Configuration:
SECRET_KEY = str(uuid.uuid4())

# Create application:
_STATIC_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              'static')

app = Flask(__name__, static_folder=_STATIC_FOLDER)
app.config.from_object(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()


_MANAGER = manager.Manager()

_ORG_PARENT_IDS = {'2157': 'Archaea',
                   '2': 'Bacteria',
                   '2759': 'Eukaryota'}

_ORGANISMS = {parent_id: organisms.get_organisms(parent_id)
              for parent_id in _ORG_PARENT_IDS}

DEBUG = False
TESTING = False


@app.route('/')
def home():
    '''Renders homepage.'''
    return app.send_static_file('index.html')


@app.route('/<path:path>')
def get_path(path):
    '''Renders homepage.'''
    return_path = path if path.startswith('export') else 'index.html'
    return app.send_static_file(return_path)


@app.route('/submit', methods=['POST'])
def submit():
    '''Responds to submission.'''
    return json.dumps({'job_ids': _MANAGER.submit(request.data)})


@app.route('/submit_sbol', methods=['POST'])
def submit_sbol():
    '''Responds to submission.'''
    filenames = []

    for file in request.files.getlist('sbol'):
        filename = secure_filename(file.filename)
        filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filename)
        filenames.append(filename)

    taxonomy_id = request.form['taxonomy_id']

    return json.dumps({'job_ids':
                       _MANAGER.submit(filenames, taxonomy_id, True)})


@app.route('/progress/<job_id>')
def progress(job_id):
    '''Returns progress of job.'''
    return Response(_MANAGER.get_progress(job_id),
                    mimetype='text/event-stream')


@app.route('/cancel/<job_id>')
def cancel(job_id):
    '''Cancels job.'''
    return _MANAGER.cancel(job_id)


@app.route('/groups/', methods=['POST'])
def get_groups():
    '''Gets groups from search term.'''
    try:
        ice_client = _connect_ice(request)
        data = json.loads(request.data)

        return json.dumps([group['label']
                           for group in ice_client.search_groups(data['term'])
                           if data['term'] in group['label']])
    finally:
        ice_client.close()


@app.route('/organism_parents/')
def get_organism_parents():
    '''Get organism parents.'''
    return json.dumps(_ORG_PARENT_IDS)


@app.route('/organisms/', methods=['POST'])
def get_organisms():
    '''Gets organisms from search term.
    Updated to assume r_rna corresponds to most prevalent
    See https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6107228/.'''
    query = json.loads(request.data)

    data = [{'taxonomy_id': taxonomy_id,
             'name': name,
             'r_rna': 'acctccttt'}
            for name, taxonomy_id in _ORGANISMS[query['parent_id']].items()
            if query['term'].lower() in name.lower()]

    return json.dumps(data)


@app.route('/restr_enzymes')
def get_restr_enzymes():
    '''Gets supported restriction enzymes.'''
    return json.dumps([str(enz) for enz in Restriction.AllEnzymes])


@app.route('/ice/connect', methods=['POST'])
def connect_ice():
    '''Connects to ICE.'''
    try:
        _connect_ice(request)
        return json.dumps({'connected': True})
    except ConnectionError as err:
        message = 'Unable to connect. Is the URL correct?'
        status_code = 503
    except net_utils.NetworkError as err:
        message = 'Unable to connect. Are the username and password correct?'
        status_code = err.get_status()

    response = jsonify({'message': message})
    response.status_code = status_code
    return response


@app.route('/ice/search/', methods=['POST'])
def search_ice():
    '''Search ICE.'''
    try:
        ice_client = _connect_ice(request)
        data = json.loads(request.data)
        resp = ice_client.advanced_search(data['term'], data['type'], 16)
        return json.dumps([result['entryInfo']['partId']
                           for result in resp['results']
                           if data['term'] in result['entryInfo']['partId']])
    except ConnectionError as err:
        message = 'Unable to connect. Is the URL correct?'
        status_code = 503
    except net_utils.NetworkError as err:
        message = 'Unable to connect. Are the username and password correct?'
        status_code = err.get_status()

    response = jsonify({'message': message})
    response.status_code = status_code
    return response


@app.route('/uniprot/<query>')
def search_uniprot(query):
    '''Search Uniprot.'''
    fields = ['entry name', 'protein names', 'sequence', 'ec', 'organism',
              'organism-id']
    result = uniprot_utils.search_uniprot(query, fields)
    return json.dumps(result)


@app.route('/export', methods=['POST'])
def export_order():
    '''Export order.'''
    ice_client = _connect_ice(request)
    data = json.loads(request.data)['designs']
    dfs = export.export(ice_client, data)

    return _save_export(dfs)


@app.errorhandler(Exception)
def handle_error(error):
    '''Handles errors.'''
    app.logger.error('Exception: %s', (error))
    traceback.print_exc()

    response = jsonify({'message': traceback.format_exc()})
    response.status_code = 500
    return response


def _connect_ice(req):
    '''Connects to ICE.'''
    data = json.loads(req.data)

    return ice_utils.get_ice_client(data['ice']['url'],
                                    data['ice']['username'],
                                    data['ice']['password'])


def _save_export(dfs):
    '''Save export file, returning the url.'''
    file_id = str(uuid.uuid4()).replace('-', '_')
    dir_name = os.path.join(os.path.join(_STATIC_FOLDER, 'export'), file_id)

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    for df in dfs:
        df.to_csv(os.path.join(dir_name, df.name + '.csv'), index=False)

    zip_file = os.path.join(dir_name + '.zip')

    with zipfile.ZipFile(zip_file, 'w') as zf:
        for dirpath, _, filenames in os.walk(dir_name):
            for filename in filenames:
                zf.write(os.path.join(dirpath, filename), filename)

    return json.dumps({'path': 'export/' + file_id + '.zip'})


def main(argv):
    '''main method.'''
    if argv:
        app.run(host='0.0.0.0', threaded=True, port=int(argv[0]),
                use_reloader=False)
    else:
        app.run(host='0.0.0.0', threaded=True, use_reloader=False)


if __name__ == '__main__':
    main(sys.argv[1:])
