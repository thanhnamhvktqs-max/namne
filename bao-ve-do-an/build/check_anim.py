"""Kiem tra cau truc hieu ung: spTgt phai tro toi shape cap tren cung; bldP chi cho p:sp; id cTn duy nhat;
dem so lan nhap moi slide; kiem tra transition va ten Morph."""
import sys, zipfile, re
from lxml import etree
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
z = zipfile.ZipFile(sys.argv[1])
pres = etree.fromstring(z.read('ppt/presentation.xml'))
rels = etree.fromstring(z.read('ppt/_rels/presentation.xml.rels'))
rmap = {r.get('Id'): r.get('Target') for r in rels}
order = [rmap[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')] for s in pres.find('p:sldIdLst', NS)]
bad = 0
total_clicks = 0
for i, t in enumerate(order, 1):
    x = etree.fromstring(z.read('ppt/' + t))
    tree = x.find('.//p:cSld/p:spTree', NS)
    top = {}
    for ch in tree:
        c = ch.find('.//p:cNvPr', NS)
        if c is not None:
            top[c.get('id')] = etree.QName(ch).localname
    allids = {}
    for c in tree.iter('{%s}cNvPr' % NS['p']):
        allids.setdefault(c.get('id'), 0)
        allids[c.get('id')] += 1
    dup = [k for k, v in allids.items() if v > 1]
    tgts = [e.get('spid') for e in x.iterfind('.//p:spTgt', NS)]
    nested = sorted({s for s in tgts if s not in top})
    ctn = [e.get('id') for e in x.iterfind('.//p:cTn', NS)]
    dupctn = len(ctn) != len(set(ctn))
    bld = [(e.get('spid'), e.get('grpId')) for e in x.iterfind('.//p:bldLst/p:bldP', NS)]
    bld_nonsp = [s for s, g in bld if top.get(s) != 'sp']
    clicks = 0
    for par in x.iterfind('.//p:cTn[@nodeType="mainSeq"]/p:childTnLst/p:par', NS):
        conds = par.find('p:cTn/p:stCondLst', NS)
        if conds is not None and len(conds) == 1 and conds[0].get('delay') == 'indefinite':
            clicks += 1
    total_clicks += clicks
    tr = x.find('p:transition', NS)
    ac = x.find('{http://schemas.openxmlformats.org/markup-compatibility/2006}AlternateContent')
    kind = 'morph' if ac is not None else (etree.QName(tr[0]).localname if tr is not None and len(tr) else 'none')
    names = [c.get('name') for c in tree.iter('{%s}cNvPr' % NS['p']) if (c.get('name') or '').startswith('!!')]
    flag = ''
    if nested or dupctn or bld_nonsp or dup:
        flag = f'  <-- nested={nested} dupctn={dupctn} bld_nonsp={bld_nonsp} dupIds={dup}'
        bad += 1
    print(f'slide {i:2d}: clicks={clicks:2d} effects={len(tgts):3d} transition={kind:6s} morphnames={len(names):2d}{flag}')
print('total clicks', total_clicks, 'problems', bad)
