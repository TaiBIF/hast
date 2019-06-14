#!/usr/bin/env python
# -.- coding: utf-8 -.-

import os
import sys
import subprocess
import re

IMG_SRC = '/Users/moogoolee/mgd/bucket/hast-img'
#ID_SRC_FILE = 'asteraceae'

def find_image(ID_LIST, file_id):
    a = 0
    b = 0
    id_list_found = []
    target_dir = 'dist/{}'.format(file_id)
    os.mkdir(target_dir)
    for root, dirs, files in os.walk(IMG_SRC):
        for i in files:
            a += 1
            m = re.search(r'S_([0-9]+)\.(JPG|jpg)', i)
            if m:
                id_ = m.group(1)
                for j in ID_LIST:
                    id_exist = '{:06d}'.format(int(j))
                    if id_ == id_exist:
                        id_list_found.append(int(id_exist))
                        src_path = os.path.join(root, i)
                        #print (src_path)
                        subprocess.call(['cp', src_path, target_dir])
                        b += 1
            #if a % 1000 == 0:
                #print ('counting... {}'.format(a))

    print (b, len(ID_LIST))
    print (set(ID_LIST).difference(set(id_list_found)))


def main(id_src_file):
    # fetch id list
    f = open('{}.txt'.format(id_src_file))
    id_list = []
    for i in f:
        id_list.append(int(i.strip()))
    find_image(id_list, id_src_file)


if len(sys.argv) < 2:
    print ('fetch-images.py [ID_SRC_FILE].txt')
else:
    main(sys.argv[1])

