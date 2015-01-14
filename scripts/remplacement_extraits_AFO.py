# coding: utf-8
"""
Copie les fichiers listés dans "Campagne num° 2012-13.xlsx" (chemin : filepath)
depuis dir_source vers dir_dest.
"""

from __future__ import print_function
import os
import shutil
import pandas as pd
from scripts.import_AFO_11_2014 import path, NOM_FICHIER, REMARQUE, EXCL_MSG


def run(dir_source, dir_dest, file_path):
    dir_source, dir_dest = map(os.path.normpath, (dir_source, dir_dest))
    df = pd.read_excel(file_path, 1,
                       encoding=u'utf-8', parse_cols=u'M,N')
    df = df[df[NOM_FICHIER].notnull() & (df[REMARQUE] != EXCL_MSG)]
    n = len(df)*2
    i = 0
    for ext in (u'mp4', u'ogg'):
        for s in df[NOM_FICHIER]:
            i += 1
            shutil.copyfile(path(dir_source, s, ext),
                            dir_dest + u'/' + s + u'.' + ext)
            print('Remplacements : %s / %s' % (i, n), end=u'\r')
