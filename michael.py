"""."""
import os
import tempfile
import unittest
import converter
from converter import ConverterObject
from utlis import url_parser, dicttoxml


class ConverterTestCase(unittest.TestCase):
    """Converter TestCase."""

    def setUp(self):  # noqa
        self.input_file = "data/hotels.csv"
        self.rows = [{
            "name": "Dörr",
            "address": "Some address",
            "stars": "3",
            "contact": "Some contact",
            "phone": "Some phone number",
            "uri": "http://www.example.com"
        }, {
            "name": "test2",
            "address": "Some address2",
            "stars": "7",
            "contact": "Some contact2",
            "phone": "Some phone number2",
            "uri": "http://www.example2.com"
        }, {
            "name": "test3",
            "address": "Some address3",
            "stars": "-3",
            "contact": "Some contact3",
            "phone": "Some phone number3",
            "uri": "http://www.example3.com"
        }]
        self.converter = ConverterObject(self.input_file)

    def test_negative_star_rating(self):   # noqa
        with self.assertLogs('converter', level='INFO') as info_log:
            star_valid = self.converter.validate_data(self.rows[2])
            self.assertFalse(star_valid)
        self.assertEqual(
            info_log.output,
            ['INFO:converter:test3 hotel with star '
                '-3 not within star range 0-5']
        )

    def test_above_range_star_rating(self):   # noqa
        star_valid = self.converter.validate_data(self.rows[1])
        self.assertFalse(star_valid)

    def test_correct_star_rating(self):   # noqa
        star_valid = self.converter.validate_data(self.converter.rows[0])
        self.assertTrue(star_valid)

    def write_to_file(self, method, ext):   # noqa
        tempfile_path = tempfile.mkstemp(suffix=ext)[1]
        try:
            method(tempfile_path)
            contents = open(tempfile_path).read()
        finally:
            os.remove(tempfile_path)
        return contents

    def test_write_to_json_or_xml(self):   # noqa
        contents = self.write_to_file(self.converter.to_json, '.json')
        self.assertTrue("{" and "name" in contents)

    def test_write_to_xml(self):   # noqa
        contents = self.write_to_file(self.converter.to_xml, '.xml')
        self.assertTrue("<name>" and "</name>" in contents)

    def test_wrong_sort_key(self):   # noqa
        with self.assertLogs('converter', level='INFO') as info_log:
            self.converter.sort_data("fake_key")
        self.assertEqual(
            info_log.output,
            ['ERROR:converter:Error - fake_key is not a valid key'])


class UrlParseTestCase(unittest.TestCase):
    """Url validation TestCase."""

    def test_url_parser_rejects_bad_url(self):
        """Test that a bad url returns False."""
        parser = url_parser.is_valid_url("some_bad_url")
        self.assertFalse(parser)

    def test_ur_parser_accepts_good_url(self):
        """Test that a valid url returns True."""
        parser = url_parser.is_valid_url("https://www.example.com")
        self.assertTrue(parser)

    def test_url_accepts_ip(self):
        """Test that an ip address url returns True."""
        parser = url_parser.is_valid_url("https://168.172.58.24")
        self.assertTrue(parser)


class DicttoXMLTestCase(unittest.TestCase):
    """TestCase for xml conversion."""

    def setUp(self):   # noqa
        self.data = [{
            "name": "test",
            "address": "Some address",
            "stars": "2",
            "contact": "Some contact",
            "phone": "Some phone number",
            "uri": "http://www.example.com"
        }]

    def test_valid_xml(self):   # noqa
        result_list = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<name> test </name>',
            '<address> Some address </address>',
            '<stars> 2 </stars>',
            '<contact> Some contact </contact>',
            '<phone> Some phone number </phone>'
        ]
        to_xml = dicttoxml.list_to_xml(self.data)
        for xml_item in result_list:
            self.assertTrue(xml_item in to_xml)


if __name__ == '__main__':
    unittest.main()