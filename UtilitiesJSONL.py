import regex
import json
import xmltodict
import pandas as pd
import PySparkUtil.Miscellaneous as SparkMisc
import PySparkUtil.PDF.UtilitiesCommon as PDFUtil


class JSONLUtilities(PDFUtil._CommonUtilities):

    def __init__(self, file: str):
        self.file_path = file
        self.outfile = SparkMisc.file_rename(file, '.jsonl')

    def __enter__(self):
        self.tracker_start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.tracker_stop('Jsonl')
        if exc_type:
            self.log('Jsonl', exc_value)
            return False
        return True

    def json_to_jsonl(self):
        """
            Reads json file
            Converts json to jsonl

            Returns: None
        """
        with open(self.file_path,) as js:
            content = json.loads(js.read())

        with open(self.outfile, 'w') as f:
            if isinstance(content, list):
                for entry in content:
                    json.dump(entry, f)
                    f.write('\n')
            else:
                json.dump(content, f)

    def csv_to_jsonl(self):
        """
            Converts csv to json and then to create json lines

            Returns: None
        """
        df = pd.read_csv(self.file_path)
        df_json = df.to_json(orient='records', force_ascii=True)
        content = json.loads(df_json)

        with open(self.outfile, 'w') as f:
            for entry in content:
                json.dump(entry, f)
                f.write('\n')

    def xml_to_jsonl(self):
        """
            Converts xml to json and then to create json lines

            Returns: None
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            my_xml = file.read()

        xml_dict = xmltodict.parse(my_xml)
        content = json.dumps(xml_dict)
        content = json.loads(content)

        with open(self.outfile, 'w') as f:
            if isinstance(content, list):
                for entry in content:
                    json.dump(entry, f)
                    f.write('\n')
            else:
                json.dump(content, f)

    def excel_to_jsonl(self):
        """
        Converts excel to json and then to create json lines

        Returns: None
        """
        df = pd.read_excel(self.file_path)
        df_json = df.to_json(orient='records', force_ascii=True)
        content = json.loads(df_json)

        with open(self.outfile, 'w') as f:
            for entry in content:
                json.dump(entry, f)
                f.write('\n')

    def convert_to_jsonl(self):
        """Converts files to JSON Lines format

                Args:
                    file_path (str): Document path

                Returns:
                    dict: filename or exception message
        """

        if regex.search(r'\.(json)$', self.file_path, regex.IGNORECASE) is not None:
            self.json_to_jsonl()
        elif regex.search(r'\.(csv)$', self.file_path, regex.IGNORECASE) is not None:
            self.csv_to_jsonl()
        elif regex.search(r'\.(xml)$', self.file_path, regex.IGNORECASE) is not None:
            self.xml_to_jsonl()
        elif regex.search(r'\.(xlsx|xls)$', self.file_path, regex.IGNORECASE) is not None:
            self.excel_to_jsonl()
        else:
            raise ValueError('Source File format is not supported.')

        return self.outfile
