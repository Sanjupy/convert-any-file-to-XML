"""Python Script that converts files from one format to another."""

import argparse
import csv
import json
import logging
import sys
import dicttoxml  
import utlis


try:
    from utlis import dicttoxml, url_parser
except ImportError:

    from yattag import indent


log = logging.getLogger(__name__)
output_handler = logging.StreamHandler(sys.stdout)
log.addHandler(output_handler)
log.setLevel(logging.INFO)


class ConverterObject(object):
    """File Conversion Object.

    Converts data in a csv file to various formats. (e.g json, xml)

    Compulsory args: input_file
    Optional args: delimiter

    """

    def __init__(self, input_file, delimiter=','):   # noqa
        self.input_file = input_file
        self.delimiter = delimiter
        self.rows = []
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=self.delimiter)
                for row in reader:
                    if ConverterObject.validate_data(row):
                        self.rows.append(row)
        except FileNotFoundError:  # catch file not found error
            log.error("Error - Input File Not Found")

    @staticmethod
    def validate_data(data):
        """Validate the URI and Rating for all rows in csv.

        Rating: Stars must have a value from 0-5.

        URI: Uri must be in a valid format.
        """
        url = data.get("uri", "")
        if url_parser.is_valid_url(url) is None:
            log.info("%s hotel with url %s is not valid" % (
                data["name"], data["uri"]))
            return False

        rating = int(data.get("stars", 0))
        if rating < 0 or rating > 5:
            log.info("%s hotel with star %s not within star range 0-5" % (
                data["name"], rating))
            return False
        return True

    def sort_data(self, sort_key):
        """Sort all dicts in the rows array by the given sort_key."""
        try:
            self.rows = sorted(self.rows, key=lambda hotels: hotels[sort_key])
        except KeyError:
            log.error("Error - %s is not a valid key", sort_key)

    def to_json(self, out_file):
        """Write json data into a new json file defined as output_file."""
        if out_file.endswith('.json'):
            with open(out_file, 'w', encoding="utf-8") as output:
                json.dump(
                    self.rows,
                    output, indent=4, sort_keys=True, ensure_ascii=False
                )
                log.info("INFO - %s created successfully", out_file)
        else:
            log.error("ERROR - Invalid output file type. Please specify json output file")  # noqa

    def to_xml(self, out_file):
        """Write xml data into a new xml file defined as output_file."""
        if out_file.endswith('.xml'):
            xml_value = dicttoxml.list_to_xml(
                self.rows, "hotels", "hotel")
            with open(out_file, 'w') as fp:
                fp.write(indent(xml_value))
                log.info("INFO - %s created successfully", out_file)

        else:
            log.error("ERROR - Invalid output file type. Please specify xml output file")   # noqa


def parse_arguments():
        """Argument Parser.

        Compulsory Args: inputFile, --output_file or -o.

        Optional Args: --delimiter or -d, --sort or -s.
        """
        parser = argparse.ArgumentParser(description="File Converter arg parser")   # noqa
        parser.add_argument(
            'inputFile',
            help='The file to be read')
        parser.add_argument(
            '--delimiter', '-d',
            default=',', help='The delimiter used in the CSV')
        parser.add_argument(
            '--output_file', '-o',
            required=True, help='File to be written into')
        parser.add_argument('--sort', '-s', help='sort key in which data will be sorted by')

        args = parser.parse_args()
        return args


def main():  # noqa
    args = parse_arguments()
    read_data = ConverterObject(args.inputFile)

    if args.sort:
        read_data.sort_data(args.sort)

    # Ensure output files are saved to data directory
    output_file = args.output_file if 'data' in args.output_file else 'data/' + args.output_file   # noqa

    # Extensible dict that adds format functions
    formats = {"json": read_data.to_json, "xml": read_data.to_xml}
    format_function = formats.get(args.output_file.split(".")[-1], None)
    if format_function:
        format_function(output_file)
    else:
        log.info("INFO - File type conversion not supported yet")
        if __name__ == '__main__':
            main()

# Note that noqa used in this script means No Quality Assurance.
# It is used to bypass some pep8 errors especially on functions without
# docstrings or long lines.