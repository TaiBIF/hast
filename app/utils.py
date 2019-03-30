#!/usr/bin/env python
# -.- coding: utf-8 -.-

# Dwc
def default_header_list():
    map_sort = [
        ('ID', '系統id'),
        ('UnitID', '館號'),
        ('_ScientificName', '學名'),
        ('_ScientificNameHast', '標籤學名'),
        ('informalName', '中文名'),
        ('_familyZH', '科名'),        
        ('_family', '科名'),
        ('_genusZH', '屬名'),                
        ('_genus', '屬名'),
        #('Identifications', '鑑定歷史'),
        ('Gathering_Agents_0_Person_ZH', '採集者(中文)'),                
        ('Gathering_Agents_0_Person', '採集者(英文)'),        
        ('FieldNumber', '採集號'),
        ('Identification_Identifiers_0_ZH', '鑑定者(中文)'),
        ('Identification_Identifiers_0', '鑑定者(英文)'),
        ('_GatheringDate', '採集日期'),
        ('_comp', '隨同人員'),
        ('_comp_en', '隨同人員(英文)'),
        ('_country', '國家'),
        ('_area', '行政區(省/縣市/鄉鎮)'),
        ('_area_en', '行政區-省/縣市/鄉鎮(英文)'),
        ('_locality', '地點'),
        ('_locality_detail', '詳細地點'),
        ('_locality_detail_en', '詳細地點(英文)'),
        ('_geo_lng', 'WGS84 Lng'),
        ('_geo_lat', 'WGS84 Lat'),
        ('_alt', '海拔')
    ]
    return [ {'key': x[0], 'label': x[1], 'alphabet': chr(65+i) } for i, x in enumerate(map_sort)]
