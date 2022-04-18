import argparse
import csv
from datetime import datetime
import os

from blabel import LabelWriter


class TCGPlayerShippingLabelWriter:
    """
    Initalize the class with a path to the tcg order csv file exported from sellers page
    Also provide a `return_address.txt` file in the project folder with desired return address
    Output a pdf file of 4x6 shipping labels for each order in csv file for use with regular postage PWE
    """

    def __init__(self, order_file):
        self.order_file = order_file
        self.read_return_address()

    def read_tcg_orders(self) -> list(dict()):
        with open(self.order_file, 'r') as f:
            reader = csv.DictReader(f, delimiter=',')
            data = [row for row in reader]

            return data

    def html_formatting(self, msgStr) -> str:
        """ Need to replace newlines/whitespace characters from python string to export to html label template """
        msgStr = msgStr.replace(' ','&nbsp;')
        msgStr = msgStr.replace('\n','<br />')
        msgStr = msgStr.replace('\t','&nbsp;&nbsp;&nbsp;&nbsp;')

        return msgStr

    def read_return_address(self) -> str:
        """ store contents of `return_address.txt` file provided """
        return_address = ''
        with open('return_address.txt', 'r') as f:
            for line in f:
                return_address += line

        self.return_address =  self.html_formatting(return_address)

    def format_address(self, row) -> str:
        """ Format each row of tcg orders csv file as shipping address """

        address_formatted = []
        name = self.html_formatting(f'{row["FirstName"]} {row["LastName"]}\n')
        address_formatted.append(name)
        street_address = self.html_formatting(f'{row["Address1"]}')
        if row['Address2'] is not None and  row['Address2'] != 'None':
            street_address += self.html_formatting(f' {row["Address2"]}')
        address_formatted.append(street_address)
        city_state_zip = self.html_formatting(f'{row["City"]}, {row["State"]} {row["PostalCode"]}\n')
        address_formatted.append(city_state_zip)
        country = self.html_formatting(row['Country'])
        address_formatted.append(country)

        return address_formatted

    def uniquify_filename(self, path) -> os.path:
        """ Don't overwrite existing files, just format new files with a counter """
        filename, extension = os.path.splitext(path)
        counter = 1

        while os.path.exists(path):
            path = filename + " (" + str(counter) + ")" + extension
            counter += 1

        return path

    def create_labels(self) -> None:
        """ top level. Read data and create list of records to export to html """
        self.order_data = self.read_tcg_orders()

        label_writer = LabelWriter("label_template.html",
                                default_stylesheets=("style.css",))

        records = list()
        for row in self.order_data:
            s_addr = self.format_address(row)
            records.append(dict(return_address=self.return_address, sending_address=s_addr))

        label_filename = f'tcg_labels_{datetime.today():%m-%d-%Y}.pdf'
        label_filename = self.uniquify_filename(label_filename)

        label_writer.write_labels(records, target=label_filename)



if __name__ == "__main__":    
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--order-file', required=True)
    args = parser.parse_args()

    order_file = args.order_file
    writer = TCGPlayerShippingLabelWriter(order_file)

    writer.create_labels()


    

    
    

    