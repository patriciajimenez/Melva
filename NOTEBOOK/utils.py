from bson import decode_all
from cycler import cycler
from matplotlib import pyplot as plt, rcParams, colors
from os import listdir
from pandas import DataFrame
from pickle import load
from tablextract import download_file
from traceback import print_exc

rcParams['pdf.fonttype'] = 3
rcParams['font.family'] = 'Cambria2'
rcParams['font.serif'] = ['Cambria2']
rcParams['font.size'] = 16
rcParams['figure.figsize'] = (12, 5)
rcParams['axes.prop_cycle'] = cycler('color', plt.cm.bone_r([.2, .4, .6, .8, 1]))
rcParams['image.cmap'] = 'bone_r'

PATH_DUMP = '../DATA/tomate/%s.bson'
PATH_TABLES = PATH_DUMP % 'tables'
PATH_ANNOTATIONS = PATH_DUMP % 'annotations'
PATH_COMMENTS = PATH_DUMP % 'comments'
PATH_ORIGINAL_TABLES = '../DATA/original_tables'  # paths of the tablextract Table objects
PATH_ORIGINAL_TABLE = PATH_ORIGINAL_TABLES + '/%s.pk'
PATH_METADATA_CORPUS = '../DATA/text-metadata-dict.pk'

DEFAULT_IGNORE_TAGS = ('Non-data', 'Multiple tables', 'Not English', 'Odd layout', 'Bug', 'Segmentation error')
DEFAULT_IGNORE_KINDS = ('unknown', 'enumeration')
FUNCTION_NAMES = {
    -1: 'empty',
    0: 'data',
    1: 'meta-data',
    2: 'context',
    3: 'decorator',
    4: 'total',
    5: 'indexer',
    6: 'factorised'
}
FUNCTION_NAMES_EXPERIMENTATION = {
    -1: 'ignore',
    0: 'data',
    1: 'meta-data',
    2: 'ignore',
    3: 'ignore',
    4: 'data',
    5: 'meta-data',
    6: 'data'
}
FUNCTION_NAMES_PREDICTION = {
    -1: 'data',
    0: 'data',
    1: 'meta-data',
    2: 'data',
    3: 'data',
    4: 'data',
    5: 'meta-data',
    6: 'data'
}
with open(PATH_METADATA_CORPUS, 'rb') as fp:
    METADATA_CORPUS = load(fp)

def load_tables(
    ignore_tags=DEFAULT_IGNORE_TAGS,
    ignore_kinds=DEFAULT_IGNORE_KINDS,
    ignore_not_annotated=True,
    ignore_commented=False,
    ignore_not_stored=True,
    function_names=None,
    verbose=True
):
    def pt(*args, **kwargs):
        if verbose: print(*args, **kwargs)

    pt('Loading tables... ', end='')
    with open(PATH_TABLES, 'rb') as fp:
        res = decode_all(fp.read())
    pt('%d loaded.' % len(res))

    if ignore_not_annotated:
        pt('Loading annotations... ', end='')
        with open(PATH_ANNOTATIONS, 'rb') as fp:
            annotations = decode_all(fp.read())
        pt('%d loaded.' % len(annotations))
        pt('Ignoring tables with no annotations... ', end='')
        annotated = set(ann['table_id'] for ann in annotations)
        res = [t for t in res if t['_id'] in annotated]
        del annotated
        pt('%d tables remain.' % len(res))
        pt('Replacing kind and function with annotated ones... ', end='')
        for table in res:            
            ann = [a for a in annotations if a['table_id'] == table['_id']]
            ann = next(reversed(sorted(ann, key=lambda a: a['date'])))
            table['kind'] = ann['kind']
            table['functions'] = ann['functions']
        del annotations
        pt('done.')

    if ignore_tags:
        pt('Ignoring tables with any of these tags: (%s)... ' % ', '.join(ignore_tags), end='')
        res = [
            t for t in res
            if not any(tag in t['tags'] for tag in ignore_tags)
        ]
        pt('%d tables remain.' % len(res))

    if ignore_kinds:
        pt('Ignoring tables with any of these kinds: (%s)... ' % ', '.join(ignore_kinds), end='')
        res = [t for t in res if t['kind'] not in ignore_kinds]
        pt('%d tables remain.' % len(res))

    if ignore_commented:
        pt('Loading comments... ', end='')
        with open(PATH_COMMENTS, 'rb') as fp:
            comments = decode_all(fp.read())
        pt('%d loaded.' % len(comments))
        pt('Ignoring tables with comments... ', end='')
        comments = set(c['table_id'] for c in comments)
        res = [t for t in res if t['_id'] not in comments]
        del comments
        pt('%d tables remain.' % len(res))

    if ignore_not_stored:
        pt('Ignoring tables with no source file stored... ', end='')
        stored_fnames = listdir(PATH_ORIGINAL_TABLES)
        res = [
            t for t in res
            if '%s.pk' % t['_id'] in stored_fnames
        ]
        pt('%d tables remain.' % len(res))

    if function_names is not None:
        pt('Renaming functions to (%s)... ' % ', '.join(set(function_names.values())), end='')
        for table in res:
            table['functions'] = [
                [function_names[cell] for cell in row]
                for row in table['functions']
            ]
        pt('done.')

    return res