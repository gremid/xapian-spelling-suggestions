#!/usr/bin/env python3

import csv
import unittest

from collections import defaultdict
from pathlib import Path
from shutil import rmtree

import xapian

# test fails with default distance of 2
levenshtein_distance = 3

class TestSpellingCorrection(unittest.TestCase):
    def setUp(self):
        db_path = Path('db')
        if db_path.is_dir():
            rmtree(db_path)

        self.testdata = defaultdict(list)
        with open('testdata.csv', newline='') as td:
            for tdi, tdr in enumerate(csv.reader(td)):
                if tdi == 0:
                    # skip header
                    continue
                title, misspelling, *_ = tdr
                self.testdata[title].append(misspelling)



        database = xapian.WritableDatabase(
            db_path.as_posix(), xapian.DB_CREATE_OR_OPEN
        )
        database.set_metadata('valuesmap', 'title:0;targetPath:1')
        database.set_metadata('kind', 'title')
        database.set_metadata('data', 'fullPath')
        database.set_metadata('language', 'english')

        stemmer = xapian.Stem('english')

        indexer = xapian.TermGenerator()
        indexer.set_stemmer(stemmer)
        indexer.set_stemming_strategy(xapian.TermGenerator.STEM_SOME)

        for title in self.testdata.keys():
            doc = xapian.Document()
            doc.set_data(title)
            doc.add_value(0, title)
            doc.add_value(1, title)
            doc.add_term(title)
            indexer.set_document(doc)
            indexer.index_text(title)
            database.add_document(doc)
            # also add title to the spelling dictionary
            database.add_spelling(title)

        database.commit()
        database.close()

        self.database = xapian.Database(db_path.as_posix())
        self.query_parser = xapian.QueryParser()
        self.query_parser.set_database(database)
        self.query_parser.set_stemmer(stemmer)
        self.query_parser.set_stemming_strategy(xapian.TermGenerator.STEM_SOME)

    def tearDown(self):
        self.database.close()

    def test_spelling_correction(self):
        for title, misspellings in self.testdata.items():
            for misspelling in misspellings:
                # query with the misspelled title
                query = self.query_parser.parse_query(misspelling)
                enquire = xapian.Enquire(self.database)
                enquire.set_query(query)
                matches = enquire.get_mset(0, 1)
                # assert no results
                self.assertEqual(matches.size(), 0)
                # retrieve spelling suggestion, asserting it equals the title
                corrected = self.database.get_spelling_suggestion(
                    misspelling, levenshtein_distance
                )
                self.assertEqual(corrected.decode('utf-8'), title, misspelling)

if __name__ == '__main__':
    unittest.main()
