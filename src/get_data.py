''' Utility functions for scaling workload experiments
'''

import paraview.simple as pvs
import scaling_algos as sc
import pv_io
from global_string_identifiers import *

def create_Perlin_noise():
    """
    Constructs perlin noise
    """
    fastUniformGrid1 = pvs.FastUniformGrid(registrationName='FastUniformGrid1')
    fastUniformGrid1.WholeExtent = [0, 255, 0, 255, 0, 255]
    fastUniformGrid1.GenerateDistanceSquaredScalars = 0
    fastUniformGrid1.GenerateSwirlVectors = 0
    fastUniformGrid1.EnableSMP = 1
    fastUniformGrid1.DesiredBytesPerPiece = 65536

    perlinNoise1 = pvs.PerlinNoise(registrationName='PerlinNoise1', Input=fastUniformGrid1)
    perlinNoise1.ImplicitFunction = 'PerlinNoise'
    perlinNoise1.ScalarArrayName = 'PerlinNoise'
    perlinNoise1.ImplicitFunction.Frequency = [0.02]*3
    perlinNoise1.ImplicitFunction.Phase = [0.0]*3
    perlinNoise1.ImplicitFunction.Amplitude = 128.0

    calculator1 = pvs.Calculator(registrationName='Calculator1', Input=perlinNoise1)
    calculator1.Function = 'PerlinNoise+128.0'
    pvs.UpdatePipeline(time=0.0, proxy=calculator1)

    pvs.SaveData('data/perlinNoise.vti', calculator1, ChooseArraysToWrite=1, PointDataArrays=['PerlinNoise'], CellDataArrays=[])

    
    fastUniformGrid3 = pvs.FastUniformGrid(registrationName='FastUniformGrid3')
    fastUniformGrid3.WholeExtent = [0, 511, 0, 511, 0, 511]
    fastUniformGrid3.GenerateDistanceSquaredScalars = 0
    fastUniformGrid3.GenerateSwirlVectors = 0
    fastUniformGrid3.EnableSMP = 1
    fastUniformGrid3.DesiredBytesPerPiece = 65536

    perlinNoise3 = pvs.PerlinNoise(registrationName='PerlinNoise1', Input=fastUniformGrid3)
    perlinNoise3.ImplicitFunction = 'PerlinNoise'
    perlinNoise3.ScalarArrayName = 'PerlinNoise'
    perlinNoise3.ImplicitFunction.Frequency = [0.02]*3
    perlinNoise3.ImplicitFunction.Phase = [0.0]*3
    perlinNoise3.ImplicitFunction.Amplitude = 128.0
    
    calculator3 = pvs.Calculator(registrationName='Calculator3', Input=perlinNoise3)
    calculator3.Function = 'PerlinNoise+128.0'
    pvs.UpdatePipeline(time=0.0, proxy=calculator3)

    pvs.SaveData('data/perlinNoise512.vti', calculator3, ChooseArraysToWrite=1, PointDataArrays=['PerlinNoise'], CellDataArrays=[])

    
    fastUniformGrid2 = pvs.FastUniformGrid(registrationName='FastUniformGrid2')
    fastUniformGrid2.WholeExtent = [0, 127, 0, 127, 0, 127]
    fastUniformGrid2.GenerateDistanceSquaredScalars = 0
    fastUniformGrid2.GenerateSwirlVectors = 0
    fastUniformGrid2.EnableSMP = 1
    fastUniformGrid2.DesiredBytesPerPiece = 65536

    perlinNoise2 = pvs.PerlinNoise(registrationName='PerlinNoise2', Input=fastUniformGrid2)
    perlinNoise2.ImplicitFunction = 'PerlinNoise'
    perlinNoise2.ScalarArrayName = 'PerlinNoise'
    perlinNoise2.ImplicitFunction.Frequency = [0.04]*3
    perlinNoise2.ImplicitFunction.Phase = [0.0]*3
    perlinNoise2.ImplicitFunction.Amplitude = 128.0

    calculator2 = pvs.Calculator(registrationName='Calculator2', Input=perlinNoise2)
    calculator2.Function = 'PerlinNoise+128.0'
    pvs.UpdatePipeline(time=0.0, proxy=calculator2)

    pvs.SaveData('data/perlinNoise128.vti', calculator2, ChooseArraysToWrite=1, PointDataArrays=['PerlinNoise'], CellDataArrays=[])

    
def downsample_foot_data():
    conf_dict = dict()
    conf_dict[DATA_FILENAME] = "data/ctBones.vti"
    conf_dict[DATA_FIELDNAME] = "Scalars_"
    proxy = pv_io.read_vti(conf_dict)
    proxy129 = sc.resample_image(proxy, 0.125)
    pvs.SaveData('data/ctBones128.vti', proxy129)

def upsample_foot_data():
    conf_dict = dict()
    conf_dict[DATA_FILENAME] = "data/ctBones.vti"
    conf_dict[DATA_FIELDNAME] = "Scalars_"
    proxy = pv_io.read_vti(conf_dict)
    proxy8 = sc.resample_image(proxy, 8.0) 
    pvs.SaveData('data/ctBones512.vti', proxy8)


def convert_and_downsample_aneurysm_data():
    nrrdReader = pvs.NrrdReader(registrationName='reader', FileName='data/aneurism.nhdr')
    pvs.UpdatePipeline(time=0.0, proxy=nrrdReader)

    pvs.SaveData('data/aneurism.vti', nrrdReader)
    proxy129 = sc.resample_image(nrrdReader, 0.125)
    pvs.SaveData('data/aneurism128.vti', proxy129)

    proxy8 = sc.resample_image(nrrdReader, 8)
    pvs.SaveData('data/aneurism512.vti', proxy8)


create_Perlin_noise()
downsample_foot_data()
upsample_foot_data()
convert_and_downsample_aneurysm_data()
