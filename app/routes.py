from flask import current_app, request, render_template, redirect, url_for, jsonify
from flask import Response, send_from_directory
#import pymssql
import tempfile
from openpyxl import Workbook
from io import BytesIO
import zipfile

from app import app, db
from app.orginations import OrgHast
from app.utils import find_image_file_list

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
        for i in ['collector_id', 'sci_name', 'collect_num_1', 'collect_num_2', 'country_id', 'family_id', 'genus_id','unit_ids']:
            if request.form.get(i, ''):
                args[i] = request.form[i]
        dstr = ''
        if request.form.get('collect_date_y', ''):
            dstr = '{}{:02d}{:02d}'.format(
                request.form.get('collect_date_y'),
                1 if not request.form.get('collect_date_m') else int(request.form.get('collect_date_m')),
                1 if not request.form.get('collect_date_d') else int(request.form.get('collect_date_d')))
        if request.form.get('collect_date_y2', ''):
            dstr += '-{}{:02d}{:02d}'.format(
                request.form.get('collect_date_y2'),
                1 if not request.form.get('collect_date_m2') else int(request.form.get('collect_date_m2')),
                1 if not request.form.get('collect_date_d2') else int(request.form.get('collect_date_d2')))

        if dstr:
            args['collect_date'] = dstr
        return redirect(url_for('query', organization='hast', **args))
    elif request.method == 'GET':
        args = request.args # sanity?
        res = org.query(args=args)

        collect_date = {
            'y': '',
            'm': '',
            'd': '',
            'y2': '',
            'm2': '',
            'd2': ''
        }

        if args.get('collect_date', ''):
            cdate = args['collect_date'].split('-')
            if len(cdate) > 1:
                print (cdate)
                collect_date['y'] = cdate[0][0:4]
                collect_date['m'] = cdate[0][4:6]
                collect_date['d'] = cdate[0][6:]
                collect_date['y2'] = cdate[1][0:4]
                collect_date['m2'] = cdate[1][4:6]
                collect_date['d2'] = cdate[1][6:]
            else:
                collect_date['y'] = cdate[0:4]
                collect_date['m'] = cdate[4:7]
                collect_date['d'] = cdate[7:]

    return render_template('query.html', collector_list=collector_list, result=res, args=args, country_list=country_list, family_list=family_list, collect_date=collect_date)

@app.route('/export_excel/<organization>')
def export_excel(organization):
    args = request.args # sanity?

    #tmp = tempfile.NamedTemporaryFile()

    filename = 'hast-dump.xlsx'
    org_map = {'hast': OrgHast}
    org = org_map[organization]()
    q = org.query(args)

    wb = Workbook(write_only=True)
    ws = wb.create_sheet()
    #for h in q['headers']:
    ws.append([h['label'] for h in q['headers']])

    for row in q['rows']:
        ws.append([row[h['key']] for h in q['headers']])
    wb.save(filename)

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/export_zipped_images/<organization>')
def export_zipped_images(organization):
    args = request.args
    org_map = {'hast': OrgHast}
    org = org_map[organization]()
    q = org.query(args)

    id_list = []
    for i in q['rows']:
        id_list.append(i['UnitID'][5:])

    memory_file = BytesIO()
    file_list = find_image_file_list(id_list)
    #print (file_list)

    from flask import send_file

    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i in file_list:
            zipf.write(i)
    memory_file.seek(0)
    return send_file(memory_file,
                     attachment_filename='images.zip',
                     as_attachment=True)
