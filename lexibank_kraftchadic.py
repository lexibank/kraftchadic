# coding=utf-8
from __future__ import unicode_literals, print_function
from itertools import groupby

import lingpy
from pycldf.sources import Source
from clldutils.text import strip_chars
from clldutils.path import Path
from clldutils.misc import slug

from pylexibank.dataset import Metadata
from pylexibank.providers import qlc

SEGMENTS_REPLACEMENTS = [
    [' ',  '_'],
    ['i̵', 'i'],
    ['ì̵', 'i'],
    ['š',  'ʃ'],
    ['ƚ',  'ɬ'],
    ['ɩ̀',  'i'],
    ['ž',  'ʒ'],
    ['ǹ',  'n'],
    ['č',  'tʃ'],
    ['ɩ́',  'i'],
    ['ǰ',  'dʒ'],
    ['ɩ̄',  'iː'],
    ['ll', 'lː'],
    ['nn', 'nː'],
    ['rr', 'rː'],
    ['mm', 'mː'],
    ['í̵', 'i'],
    ['ss', 'sː'],
]

class Dataset(qlc.QLC):
    dir = Path(__file__).parent
    id = 'kraftchadic'
    DSETS = ['kraft1981.csv']

    def get_segments(self, form):
        # REPLACEMENTS, to be moved to an orthographic profile
        for source, target in SEGMENTS_REPLACEMENTS:
            form = form.replace(source, target)

        return lingpy.ipa2tokens(form, merge_vowels=False)


    def cmd_install(self, **kw):
        # column "counterpart_doculect" gives us the proper names of the doculects
        wl = lingpy.Wordlist(self.raw.posix(self.DSETS[0]), col="counterpart_doculect")

        # get the language identifiers stored in wl._meta['doculect'] parsed from input
        # file
        lids = {}
        for line in wl._meta['doculect']:
            rest = line.split(', ')
            name = rest.pop(0)
            lids[name] = rest.pop(0)

        concepts = {
            strip_chars('()?', c.english).upper().replace("'", ' '): c.concepticon_id
            for c in self.conceptlist.concepts.values()}

        src = Source.from_bibtex("""
@book{Kraft1981,
    author={Kraft, Charles H.},
    title={Chadic Wordlists.},
    year={1981},
    address={Berlin},
    publisher={D. Reimer}
}""")

        concept_map = {
            'MAT TABARME': 'MAT TABARMA'
        }

        def grouped_rows(wl):
            rows = [
                (wl[k, 'counterpart_doculect'], wl[k, 'concept'], wl[k, 'counterpart'], wl[k, 'qlcid'])
                for k in wl]
            return groupby(sorted(rows), key=lambda r: (r[0], r[1]))

        with self.cldf as ds:
            ds.add_sources(src)
            for (language, concept), rows in grouped_rows(wl):
                iso = lids[language]
                concept = concept.replace('_', ' ')
                cid = concepts[concept_map.get(concept, concept)]

                ds.add_language(
                    ID=slug(language),
                    Name=language.capitalize(),
                    ISO639P3code=lids[language],
                    Glottocode=self.glottolog.glottocode_by_iso.get(iso, ''))
                ds.add_concept(ID=cid, Name=concept, Concepticon_ID=cid)

                for i, (l, c, form, id_) in enumerate(rows):
                    ds.add_lexemes(
                        Language_ID=slug(language),
                        Parameter_ID=cid,
                        Value=form,
                        Source=[src.id],
                        Segments=self.get_segments(form),
                        Local_ID=id_)
