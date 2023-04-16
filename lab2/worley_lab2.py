# West Nile Virus Outbreak Analysis
# Use this program to identify areas at high risk for outbreaks of West Nile Virus in Boulder
# programmer: Crystal Worley, Front Range Community College

import arcpy
import yaml
from etl.GSheetsEtl import GSheetsEtl

arcpy.env.overwriteOutput = True

xMin = -179.148909
yMin = -14.548699
xMax = 179.778470
yMax = 71.365162

arcpy.env.XYDomain = f"{xMin} {yMin} {xMax} {yMax}"


def etl():
    print("Extracting, transforming, and loading...")
    etl_instance = GSheetsEtl(config_dict)
    etl_instance.process()


def setup():
    with open(r"C:\Users\cryst\gis_programming\WNVOutbreakPyProject\etl\wnvoutbreak.yaml") as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)
    return config_dict

# Buffer Analysis

def buffer(layer_name,buff_dist):
    # Buffer the incoming layer by the buffer distance.
    output_buffer_layer_name = f"buf_{layer_name}"
    print(f"Buffering {layer_name} and creating {output_buffer_layer_name}")
    arcpy.analysis.Buffer(layer_name, output_buffer_layer_name, buff_dist,"FULL","ROUND","ALL",None,"PLANAR")

    # Add new layer to map project.


# Intersect Analysis

def intersect(layers):
    # Intersect the four previously created buffer layers.
    arcpy.env.overwriteOutput = True
    output_intersect = "intersect_buffers"
    print("Intersecting buffered layers...")
    arcpy.analysis.Intersect(layers, output_intersect)


# Erase address points of people who opted out

def erase(input_layer,erase_layer,output_layer):
    # Erase the latitude and longitude points of residents who opted out of pesticide spraying.
    print("Removing point locations of opt-out residents...")
    arcpy.analysis.Erase(input_layer,erase_layer,output_layer)


# Spatial Join

def spatial_join(target_layer,join_layer):
    # Join the output intersect layer with the Boulder addresses layer.
    output_spatial_join = "final_addresses"
    print("Completing spatial join...")
    arcpy.analysis.SpatialJoin(target_layer, join_layer, output_spatial_join)


def main():
    arcpy.env.overwriteOutput = True
    buffer("lakes_and_reservoirs", "1500 feet")
    buffer("wetlands_boulder", "1500 feet")
    buffer("osmp_props", "1500 feet")
    buffer("mosq_larv_sites", "1500 feet")
    buffer("avoid_points", "1500 feet")

    list_layers = ["buf_lakes_and_reservoirs", "buf_wetlands_boulder", "buf_mosq_larv_sites",
                   "buf_osmp_props"]

    intersect(list_layers)

    erase("intersect_buffers","buf_avoid_points","addresses_wo_optouts")

    spatial_join("boulder_addresses", "addresses_wo_optouts")

    # Count the number of addresses will be notified about pesticide spraying.
    field = ['Join_Count']
    count = 0

    final_layer = 'final_addresses'
    aprx = arcpy.mp.ArcGISProject(rf"{config_dict.get('proj_dir')}\WestNileOutbreak.aprx")
    m = aprx.listMaps()[0]
    m.addDataFromPath(arcpy.env.workspace + '\\' + final_layer)
    aprx.save()

    with arcpy.da.SearchCursor(final_layer, field) as cursor:
        for row in cursor:
            if row[0] >= 1:
                count = count + 1

    print(f"{count} addresses will be notified about pesticide spraying.")

    print("Buffer, intersect, and spatial join have successfully completed.")

if __name__ == '__main__':
    global config_dict
    config_dict = setup()
    gsheetsetl = GSheetsEtl(config_dict)
    print(config_dict)
    etl()
    main()


