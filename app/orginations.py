#!/usr/bin/env python
# -.- coding: utf-8 -.-

from app.models import Hast, Person
from app.utils import default_header_list

class OrgHast(object):
    headers = []
    def __init__(self):
        self.headers = default_header_list()

    def get_collector_list(self):
        return Person.query.filter(Person.collector==True).all()
        
    def query(self, args={}):
        res = {
            'rows': [],
            'headers': self.headers,
            'menu': {
                'collectors': []
            }
        }
        # collectors        
        plist = Person.query.filter(Person.collector==True).all()
        for i in plist:
            res['menu']['collectors'].append([i.pid, '{} / {}'.format(i.name_en, i.nameC or '')])
        q = Hast.query
        order_col = ''
        #for k,v in args.items():
        # sanity key
        if args.get('collector_id', '') and args['collector_id']:
            q = q.filter(Hast.collectorID==args['collector_id'])
            order_col = 'collectNum1'
        if args.get('collect_num_1', '') and args.get('collect_num_2', ''):
            order_col = 'collectNum1'
            q = q.filter(Hast.collectNum1>=args.get('collect_num_1'),
                         Hast.collectNum1<=args.get('collect_num_2'))
        elif args.get('collect_num_1', ''):
            q = q.filter(Hast.collectNum1 == args.get('collect_num_1'))
        #a = q.limit(100)
        cnt = q.count()
        if cnt >= 2000:
            #flash
            print ('too many!')
            pass
        if order_col:
            q = q.order_by(order_col)
            
        #print (q)
        
        a = q.limit(max(cnt, 2000)) # limit 2000
        for i in a:
            speciemen_dup_list = [x.specimen for x in i.duplications if x.specimen]
            #print (i.SN, '-------------', speciemen_dup_list)
            for j in speciemen_dup_list:
                #print (i.SN,i.verifications, '======')                
                names = {
                    'sci': '',
                    'sci0': '',
                    'common': '',
                    'family': '',
                    'family_zh':'',
                    'genus': '',
                    'genus_zh':'',
                    'identifier': '',
                    'identifier_zh': '',
                }
                ## TODO 參考 ABCD 資料結構
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
                        names['common'] = v.species.speciesC if v.species else 'speciesID:{}'.format(v.speciesID)
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
                    'UnitID': 'HAST:{}'.format(j.specimenOrderNum),
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
                    '_alt': '{} - {}'.format(i.alt, i.altx) if i.altx else i.alt
                    
                }
                res['rows'].append(abcd_terms)
        return res
