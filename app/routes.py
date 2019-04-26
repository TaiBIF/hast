from flask import current_app, request, render_template, redirect, url_for, jsonify
from flask import Response, send_from_directory
#import pymssql
import tempfile
from openpyxl import Workbook

from app import app, db
from app.orginations import OrgHast

@app.route('/')
def index():
    return redirect(url_for('query', organization='hast'))

@app.route('/api/query/<organization>')
def api(organization):
    res = {}

    if organization not in ['hast']:
        res = {
            'error': 'err org'
        }
    else:
        org_map = {'hast': OrgHast}
        org = org_map[organization]()
        res = org.query()
    return jsonify(res)

@app.route('/api/query/<organization>/<taxon>/<taxon_id>')
def api_taxon(organization, taxon, taxon_id):
    res = {}

    if organization not in ['hast']:
        res = {
            'error': 'err org'
        }
    else:
        org_map = {'hast': OrgHast}
        org = org_map[organization]()
        #res = org.query()
        res = []
        if taxon == 'family':
            rows = org.get_genus_list(taxon_id)
            for i in rows:
                label = '{} /{}'.format(i.genusE.strip(), i.genusC) if i.genusC else i.genusE
                res.append([i.genusID, label])
    return jsonify(res)

@app.route('/query/<organization>', methods=['GET', 'POST'])
def query(organization):
    org_map = {'hast': OrgHast}
    org = org_map[organization]()

    collector_list= org.get_collector_list()
    country_list= org.get_country_list()
    family_list= org.get_family_list()
    args = {}
    if request.method == 'POST':
        for i in ['collector_id', 'sci_name', 'collect_num_1', 'collect_num_2', 'country_id', 'family_id', 'genus_id']:
            if request.form.get(i, ''):
                args[i] = request.form[i]
        return redirect(url_for('query', organization='hast', **args))
    elif request.method == 'GET':
        args = request.args # sanity?
        res = org.query(args=args)
    return render_template('query.html', collector_list=collector_list, result=res, args=args, country_list=country_list, family_list=family_list)

@app.route("/export_csv/<organization>")
def export_csv(organization):
    args = request.args # sanity?

    #tmp = tempfile.NamedTemporaryFile()

    filename = 'hast-dump.xlsx'
    org_map = {'hast': OrgHast}
    org = org_map[organization]()
    csv_list = []
    q = org.query(args)

    wb = Workbook(write_only=True)
    ws = wb.create_sheet()
    #for h in q['headers']:
    ws.append([h['label'] for h in q['headers']])

    for row in q['rows']:
        ws.append([row[h['key']] for h in q['headers']])
    wb.save(filename)

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
