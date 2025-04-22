from global_string_identifiers import *
import scaling_algos as sc
import pv_io as pvio
import algos as alg
import paraview.simple as pvs
import os
import sys

exp_dict = dict()

if len(sys.argv) < 2:
    print("no max threads given - this determines the scaling of the data", file=sys.stderr)
sf = float(sys.argv[1])

num_files = len(sys.argv)
for i in range(2,num_files,2):
    exp_dict = dict()
    data_path = sys.argv[i]
    if data_path[-4:] != '.vti':
        print("wrong data format - data has to be .vti", file=sys.stderr)
    path, file = os.path.split(data_path)
    name = file[:-4]
    exp_dict[DATA_FILENAME] = data_path
    exp_dict[DATA_FIELDNAME] = sys.argv[i+1]

    proxy = pvio.read_vti(exp_dict)
    scaled_data = sc.resample_image(proxy, sf)
    output_name = path + '/' + name + 'Large.vti'
    pvs.SaveData(output_name, scaled_data, ChooseArraysToWrite=1, PointDataArrays=[exp_dict[DATA_FIELDNAME]], CellDataArrays=[])
