# West Nile Virus Outbreak Analysis
# Use this program to identify areas at high risk for outbreaks of West Nile Virus in Boulder
# programmer: Crystal Worley, Front Range Community College

import arcpy
arcpy.env.overwriteOutput = True

# set the workspace and project
arcpy.env.workspace = input("Please specify the path of your arcpy workspace: ")
project_path = input("Please enter the path to your project: ")
aprx = arcpy.mp.ArcGISProject(project_path)

# Buffer Analysis

def buffer(layer_name,buff_dist):
    # Buffer the incoming layer by the buffer distance.
    output_buffer_layer_name = f"buf_{layer_name}"
    print(f"Buffering {layer_name} and creating {output_buffer_layer_name}")
    arcpy.analysis.Buffer(layer_name,output_buffer_layer_name,buff_dist,"FULL","ROUND","ALL",None,"PLANAR")

    # Add new layer to map project.

    m = aprx.listMaps()[0]
    m.addDataFromPath(arcpy.env.workspace + '\\' + output_buffer_layer_name)
    aprx.save()

# Intersect Analysis

def intersect(layers):
    # Intersect the four previously created buffer layers.
    output_intersect = "intersect_buffers"
    print("Intersecting buffered layers...")
    arcpy.analysis.Intersect(layers,output_intersect)

    m = aprx.listMaps()[0]
    m.addDataFromPath(arcpy.env.workspace + '\\' + output_intersect)
    aprx.save()

# Spatial Join

def spatial_join(target_layer,join_layer):
    # Join the output intersect layer with the Boulder addresses layer.
    output_spatial_join = "addresses_with_intersects"
    print("Completing spatial join...")
    arcpy.analysis.SpatialJoin(target_layer, join_layer, output_spatial_join)

    # EXTRA CREDIT: Count the number of addresses that fall within the intersect layer.
    field = "Join_Count"
    count = 0
    with arcpy.da.SearchCursor(output_spatial_join, field) as cursor:
        for row in cursor:
            if row[0] >= 1:
                count = count + 1

    print(f"{count} addresses fall within the intersect layer.")

    m = aprx.listMaps()[0]
    m.addDataFromPath(arcpy.env.workspace + '\\' + output_spatial_join)
    aprx.save()

if __name__ == '__main__':
    buffer("lakes_and_reservoirs", "1000 feet")
    buffer("wetlands_boulder", "1000 feet")
    buffer("osmp_props", "1000 feet")
    buffer("mosq_larv_sites", "1000 feet")

    list_layers = ["buf_lakes_and_reservoirs", "buf_wetlands_boulder", "buf_mosq_larv_sites", "buf_osmp_props"]
    intersect(list_layers)

    spatial_join("boulder_addresses", "intersect_buffers")

    print("Buffer, intersect, and spatial join have successfully completed.")

