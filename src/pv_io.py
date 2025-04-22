''' Utility functions for scaling workload experiments
'''

# from paraview.simple import *
import paraview.simple as pvs
from global_string_identifiers import *
import os
import numpy as np
import pandas as pd
from pathlib import Path
import fcntl


def read_pvti(conf_dict):
  """
  Reads data from disk according to configuration.

  Reads .pvti file given in conf_dict['filename'].

  Parameters
  ----------
  conf_dict : dict
      map containing configurations for benchmark

  Returns
  -------
  proxy
      A ParaView proxy yielding the read image
  """
  filename = conf_dict[DATA_FILENAME]
  image = pvs.XMLPartitionedImageDataReader(registrationName='image.pvti', FileName=[filename])
  image.PointArrayStatus = [conf_dict[DATA_FIELDNAME]]
  image.TimeArray = 'None'
  pvs.UpdatePipeline(time=0.0, proxy=image)
  extent = image.GetDataInformation().GetExtent()
  conf_dict[DATA_EXTENT] = extent

  return image


def read_vti(conf_dict):
  """
  Reads data from disk according to configuration.

  Reads .vti file given in conf_dict['filename'].

  Parameters
  ----------
  conf_dict : dict
      map containing configurations for benchmark

  Returns
  -------
  proxy
      A ParaView proxy yielding the read image
  """
  filename = conf_dict[DATA_FILENAME]
  image = pvs.XMLImageDataReader(registrationName='image.vti', FileName=[filename])
  image.PointArrayStatus = [conf_dict[DATA_FIELDNAME]]
  image.TimeArray = 'None'
  pvs.UpdatePipeline(time=0.0, proxy=image)
  extent = image.GetDataInformation().GetExtent()
  conf_dict[DATA_EXTENT] = extent
  
  return image


def write_dict_to_csv(in_dict):
  """
  Writes dict to csv

  Converts dict to pandas dataframe and writes to csv
  filename for csv is extracted from dict[BM_OUTPUT_FILENAME]

  Parameters
  ----------
  in_dict : dict
      dict to write to csv
  """
  conf_dict = in_dict.copy()
  assert BM_OUTPUT_FILENAME in conf_dict.keys()
  output_filename = conf_dict[BM_OUTPUT_FILENAME]
  
  for key, value in conf_dict.items():
    conf_dict[key] = [value]

  df = pd.DataFrame.from_dict(conf_dict)
  Path(os.path.split(output_filename)[0]).mkdir(parents=True, exist_ok=True)

  with open(output_filename, mode='a+') as f:
    fcntl.flock(f, fcntl.LOCK_EX)
    is_empty = f.tell() == 0
    df.to_csv(output_filename, mode='a', header=is_empty, sep=';', index=False)