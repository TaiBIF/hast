#!/usr/bin/env python
# -.- coding: utf-8 -.-

from datetime import datetime

from flask import flash
from sqlalchemy import or_
from sqlalchemy.orm import subqueryload

from app.models import Hast, Person, Species, Verification, Country, Family, Genus, Specimen, Duplication
from app.utils import default_header_list


class OrgHast(object):
    headers = []
    def __init__(self):
        self.headers = default_header_list()

    def get_collector_list(self):
        return Person.query.filter(Person.collector==True).all()

    def get_country_list(self):
        return Country.query.order_by('country').all()

    def get_family_list(self):
        return Family.query.order_by('familyE').all()

    def get_genus_list(self, family_id):
        return Genus.query.filter(Genus.familyID==family_id).order_by('genusE').all()

    def query(self, args={}):
        res = {
            'rows': [],
            'headers': self.headers,
            'menu': {
                'collectors': []
            }
        }
        a = []
        specimen_order_num_list = [] # 用館號搜尋時, 去連集, 不要找出副本
        # collectors
        plist = Person.query.filter(Person.collector==True).all()
        for i in plist:
            res['menu']['collectors'].append([i.pid, '{} / {}'.format(i.name_en, i.nameC or '')])
        q = Hast.query
        order_col = ''
        #for k,v in args.items():
        # sanity key
        #print (args)
        if args != {}:
            if args.get('collector_id', ''):
                q = q.filter(Hast.collectorID==args['collector_id'])
                order_col = 'collectNum1'
            if args.get('collect_num_1', '') and args.get('collect_num_2', ''):
                order_col = 'collectNum1'
                q = q.filter(Hast.collectNum1>=args.get('collect_num_1'),
                             Hast.collectNum1<=args.get('collect_num_2'))
            elif args.get('collect_num_1', ''):
                q = q.filter(Hast.collectNum1 == args.get('collect_num_1'))

            if args.get('sci_name', ''):
                #q = q.filter(Hast.verifications.species.speciesE.like('%{}%'.format(args['sci_name'])))
                # tricky !
                like_s = '%{}%'.format(args['sci_name'])
                species = Species.query.filter(or_(Species.speciesE.like(like_s),
                                                   Species.speciesC.like(like_s))).\
                                               all()
                species_ids = [x.speciesID for x in species]
                vers = Verification.query.filter(Verification.speciesID.in_(species_ids)).all()
                ver_ids = [x.ID for x in vers]
                q = q.filter(Hast.verifications.any(Verification.ID.in_(ver_ids)))
                #print (species_ids, 'xxxxxxxx',vers)
                #filter(Hast.verifications.speciesID.in_(species_ids))
                #q = q.filter(subqueryload(Verification.speciesID.in_(species_ids)))
            if args.get('country_id', ''):
                q = q.filter(Hast.countryNo==args['country_id'])


            if args.get('family_id', ''):
                q = q.filter(Hast.verFamilyID==args['family_id'])
            if args.get('genus_id', ''):
                q = q.filter(Hast.verGesnuID==args['genus_id'])

            if args.get('collect_date', ''):
                cdate = args['collect_date'].split('-')
                if len(cdate) > 1:
                    beg = datetime.strptime(cdate[0], '%Y%m%d')
                    end = datetime.strptime(cdate[1], '%Y%m%d')
                    q = q.filter(Hast.collectionDate>=beg, Hast.collectionDate<=end)
                else:
                    q = q.filter(Hast.collectionDate==cdate)

            if args.get('unit_ids', ''):
                # 用館號搜尋, 不要找複本
                no_dup = True
                unit_id_list = args['unit_ids'].split(',')
                specimen_order_num_list = Specimen.query.filter(Specimen.specimenOrderNum.in_(unit_id_list)).all()
                sn_list = []
                for sm in specimen_order_num_list:
                    sn_list.append(sm.duplication.SN)
                q = q.filter(Hast.SN.in_(sn_list))

            #a = q.limit(100)
            cnt = q.count()
            if cnt >= 2000:
                flash('too many, 請重設條件!')
                return res
            if order_col:
                q = q.order_by(order_col)
            a = q.limit(min(cnt, 2000)).all() # limit 2000
        else:
            a = []

        counter = 0
        for i in a:
            counter += 1
            is_name_match = True
            specimen_dup_list = [x.specimen for x in i.duplications if x.specimen]
            #print (i.SN, '-------------', specimen_dup_list, specimen_order_num_list)
            hast_dup_list = []
            if specimen_order_num_list:
                hast_dup_list = list(set(specimen_dup_list).intersection(set(specimen_order_num_list)))
            else:
                hast_dup_list = specimen_dup_list
            #print (i, hast_dup_list, counter, cnt)
            order_num = 0
            for j in hast_dup_list:
                #print (i.SN,i.verifications, '======')
                order_num = j.specimenOrderNum
                ## TODO 參考 ABCD 資料結構
                names = {
                    'sci': '',#i.verSpeciesE,
                    'sci0':'', #i.verSpeciesE,
                    'common': '',#i.verSpeciesC,
                    'family': '',#i.verFamilyE,
                    'family_zh': '',#i.verFamilyC,
                    'genus': '',#i.verGenusE,
                    'genus_zh': '',#i.verGenusC,
                    'identifier': '',
                    'identifier_zh': '',
                }
                if i.verifications:
                    ids = []
                    v0 = i.verifications[-1]
                    v = i.verifications[0]
                    if v0.speciesID:
                        if v0.speciesID:
                            names['sci0'] = v0.species.speciesE if v0.species else  'speciesID:{}'.format(v0.speciesID) # 標籤學名: 第一次鑑定
                        elif v0.genusID:
                            names['genus'] = i.verifications[-1].genus

                    if v.speciesID:
                        names['sci'] = v.species.speciesE if v.species else 'speciesID:{}'.format(v.speciesID) #最新鑑定當作學名
                        #if args.get('sci_name', ''):
                        #    if args['sci_name'] not in names['sci']:
                        #        is_name_match = False

                        names['common'] = v.species.speciesC or '' if v.species else 'speciesID:{}'.format(v.speciesID)
                        names['genus'] = v.species.genusE if v.species else ''
                        names['genus_zh'] = v.species.genusC if v.species else ''
                        names['family'] = v.family.familyE if v.family else ''
                        names['family_zh'] = v.family.familyC if v.family else ''
                    elif v.genusID:
                        if v.genus:
                            names['genus'] = v.genus.genusE
                            names['genus_zh'] = v.genus.genusC
                            names['family'] = v.family.familyE
                            names['family_zh'] = v.family.familyC
                        else:
                            names['genus'] = v.genusID
                            names['genus_zh'] = v.genusID
                            names['family'] = v.familyID
                            names['family_zh'] = v.familyID
                    elif v.familyID:
                        names['family'] = v.family.familyE if v.family else ''
                        names['family_zh'] = v.family.familyC if v.family else ''
                    #else:
                    #    print (v, '===== no ver =====')

                    if v.verifierid:
                        names['identifier_zh'] = v.verifier.nameC
                        names['identifier'] = '{} {}'.format(v.verifier.firstName, v.verifier.lastName)
                #elif args.get('sci_name', ''): # 有查詢 sci_name, 但沒有 verification
                #    is_name_match = False

                area_list = []
                if i.provinceNo:
                    area_list.append(i.province.provinceC or '')
                if i.hsienNo:
                    area_list.append(i.hsien.hsienCityC or '')
                if i.townNo:
                    area_list.append(i.town.hsiangTownC or '')

                area_en_list = []
                if i.provinceNo:
                    area_en_list.append(i.province.provinceE or '')
                if i.hsienNo:
                    area_en_list.append(i.hsien.hsienCityE or '')
                if i.townNo:
                    area_en_list.append(i.town.hsiangTownE or '')

                abcd_terms =  {
                    'ID': i.SN,
                    'UnitID': '',
                    '_ScientificName': names['sci'],
                    '_ScientificNameHast': names['sci0'],
                    '_family': names['family'],
                    '_familyZH': names['family_zh'],
                    '_genus': names['genus'],
                    '_genusZH': names['genus_zh'],
                    'informalName': names['common'],
                    'Gathering_Agents_0_Person_ZH': i.collector.nameC if i.collector else '',
                    'Gathering_Agents_0_Person': '{} {}'.format(i.collector.firstName, i.collector.lastName) if i.collector else '',
                    'FieldNumber': '{} {}'.format(i.collectNum1, i.collectNum2 or ''),
                    'Identification_Identifiers_0': names['identifier'],
                    'Identification_Identifiers_0_ZH': names['identifier_zh'],
                    'Identification_Identifiers_0': names['identifier'],
                    '_GatheringDate': i.collectionDate.strftime('%Y-%m-%d') if i.collectionDate else '',
                    '_comp': i.companion or '',
                    '_comp_en': i.companionE or '',
                    '_country': i.country.countryC if i.country else '',
                    '_area': ' / '.join(area_list),
                    '_area_en': ' / '.join(area_en_list),
                    '_locality':'',
                    '_locality_detail': i.additionalDesc or '',
                    '_locality_detail_en': i.additionalDescE or '',
                    '_geo_lng': '{}'.format(i.WGS84Lng or ''),
                    '_geo_lat': '{}'.format(i.WGS84Lat or ''),
                    '_alt': '{} - {}'.format(i.alt, i.altx) if i.altx else (i.alt or ''),
                    '_url': ''
                }

                if order_num:
                    abcd_terms['UnitID'] = 'HAST:{}'.format(order_num)
                    abcd_terms['_url'] = 'http://www.hast.biodiv.tw/specimens/SpecimenDetailC.aspx?specimenOrderNum={}'.format(order_num)

                #if is_name_match:
                res['rows'].append(abcd_terms)

        #f = open('ids.txt', 'w')
        #f.write(str([x['UnitID'] for x in res['rows']]))
        #f.close()
        return res
