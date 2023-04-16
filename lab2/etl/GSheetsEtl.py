import requests
import csv
import arcpy
from etl.SpatialEtl import SpatialEtl

class GSheetsEtl(SpatialEtl):

    config_dict = None
    def __init__(self, config_dict):
        super().__init__(config_dict)

    def extract(self):
        print("Extracting addresses from google form spreadsheet")

        r = requests.get(self.config_dict.get('remote_url'))
        r.encoding = "utf-8"
        data = r.text
        with open(f"{self.config_dict.get('proj_dir')}addresses.csv", "w") as output_file:
            output_file.write(data)

    def transform(self):
        print("Add City, State")

        transformed_file = open(rf"{self.config_dict.get('proj_dir')}\new_addresses.csv", "w")
        transformed_file.write("X,Y,Type\n")
        with open(r"C:\Users\cryst\Downloads\addresses.csv", "r") as partial_file:
            csv_dict = csv.DictReader(partial_file, delimiter=',')
            for row in csv_dict:
                address = row["Street address"] + " Boulder CO"
                print(address)
                geocoder_url = self.config_dict.get('geocoder_prefix_url') + f"{address}" + self.config_dict.get('geocoder_suffix_url')
                print(geocoder_url)
                r = requests.get(geocoder_url)

                resp_dict = r.json()
                x = resp_dict['result']['addressMatches'][0]['coordinates']['x']
                y = resp_dict['result']['addressMatches'][0]['coordinates']['y']
                transformed_file.write(f"{x},{y},Residential\n")

        transformed_file.close()

    def load(self):
        # Description: Creates a point feature class from input table

        # Set environment settings
        arcpy.env.workspace = rf"{self.config_dict.get('proj_dir')}\WestNileOutbreak.gdb"
        arcpy.env.overwriteOutput = True

        # Set the local variables
        in_table = rf"{self.config_dict.get('proj_dir')}\new_addresses.csv"
        out_feature_class = "avoid_points"
        x_coords = "X"
        y_coords = "Y"

        # Make the XY event layer...
        arcpy.management.XYTableToPoint(in_table, out_feature_class, x_coords, y_coords)

        # Print the total rows
        print(arcpy.GetCount_management(out_feature_class))

    def process(self):
        self.extract()
        self.transform()
        self.load()