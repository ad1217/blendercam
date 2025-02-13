# used by OpenCAMLib sampling

import bpy
import os
import tempfile
from subprocess import call
from cam.collision import BULLET_SCALE
from cam import simple
from cam.chunk import camPathChunk
from cam.simple import *
from shapely import geometry as sgeometry

OCL_SCALE = 1000

PYTHON_BIN = None

if os.name == "nt":
    PYTHON_BIN = "python.exe"
elif os.name == "posix":
    PYTHON_BIN = "python"


def operationSettingsToCSV(operation):
    with open(os.path.join(tempfile.gettempdir(), 'ocl_settings.txt'), 'w') as csv_file:
        csv_file.write("{}\n".format(operation.cutter_type))
        csv_file.write("{}\n".format(operation.cutter_diameter))
        csv_file.write("{}\n".format(operation.minz))


def pointsToCSV(operation, points):
    with open(os.path.join(tempfile.gettempdir(), 'ocl_chunks.txt'), 'w') as csv_file:
        for point in points:
            csv_file.write("{} {}\n".format(point[0], point[1]))


def pointSamplesFromCSV(points):
    with open(os.path.join(tempfile.gettempdir(), 'ocl_chunk_samples.txt'), 'r') as csv_file:
        for point in points:
            point[2] = float(csv_file.readline()) / OCL_SCALE
    # print(str(point[2]))


def chunkPointsToCSV(operation, chunks):
    with open(os.path.join(tempfile.gettempdir(), 'ocl_chunks.txt'), 'w')as csv_file:
        for ch in chunks:
            p_index = 0
            for point in ch.points:
                if operation.ambient.contains(sgeometry.Point(point[0], point[1])):
                    csv_file.write("{} {}\n".format(point[0], point[1]))
                else:
                    ch.points[p_index] = (point[0], point[1], 2)
                p_index += 1


def chunkPointSamplesFromCSV(chunks):
    with open(os.path.join(tempfile.gettempdir(), 'ocl_chunk_samples.txt'), 'r') as csv_file:
        for ch in chunks:
            p_index = 0
            for point in ch.points:
                if len(point) == 2 or point[2] != 2:
                    z_sample = float(csv_file.readline()) / OCL_SCALE
                    ch.points[p_index] = (point[0], point[1], z_sample)
                # print(str(point[2]))
                else:
                    ch.points[p_index] = (point[0], point[1], 1)
                p_index += 1


def resampleChunkPointsToCSV(operation, chunks_to_resample):
    with open(os.path.join(tempfile.gettempdir(), 'ocl_chunks.txt'), 'w') as csv_file:
        for chunk, i_start, i_length in chunks_to_resample:
            for p_index in range(i_start, i_start + i_length):
                csv_file.write("{} {}\n".format(chunk.points[p_index][0], chunk.points[p_index][1]))


def chunkPointsResampleFromCSV(chunks_to_resample):
    with open(os.path.join(tempfile.gettempdir(), 'ocl_chunk_samples.txt'), 'r') as csv_file:
        for chunk, i_start, i_length in chunks_to_resample:
            for p_index in range(i_start, i_start + i_length):
                z = float(csv_file.readline()) / OCL_SCALE
                if z > chunk.points[p_index][2]:
                    chunk.points[p_index][2] = z


def exportModelsToSTL(operation):
    file_number = 0
    for collision_object in operation.objects:
        activate(collision_object)
        bpy.ops.object.duplicate(linked=False)
        # collision_object = bpy.context.scene.objects.active
        # bpy.context.scene.objects.selected = collision_object
        file_name = os.path.join(tempfile.gettempdir(), "model{0}.stl".format(str(file_number)))
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.transform.resize(value=(OCL_SCALE, OCL_SCALE, OCL_SCALE), constraint_axis=(False, False, False),
                                 orient_type='GLOBAL', mirror=False, use_proportional_edit=False,
                                 proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False,
                                 snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0),
                                 texture_space=False, release_confirm=False)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.export_mesh.stl(check_existing=True, filepath=file_name, filter_glob="*.stl", use_selection=True,
                                ascii=False, use_mesh_modifiers=True, axis_forward='Y', axis_up='Z', global_scale=1.0)
        bpy.ops.object.delete()
        file_number += 1


def oclSamplePoints(operation, points):
    print(os.path.join(tempfile.gettempdir(), "oclSamplePoints\n"))
    operationSettingsToCSV(operation)
    pointsToCSV(operation, points)
    exportModelsToSTL(operation)
    if os.path.isdir(os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib")):
        call([PYTHON_BIN, os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib", "oclSample.py")])
    else:
        call([PYTHON_BIN, os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib", "oclSample.py")])
    pointSamplesFromCSV(points)


def oclSample(operation, chunks):
    operationSettingsToCSV(operation)
    chunkPointsToCSV(operation, chunks)
    exportModelsToSTL(operation)
    if os.path.isdir(os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib")):
        call([PYTHON_BIN, os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib", "oclSample.py")])
    else:
        call([PYTHON_BIN, os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib", "oclSample.py")])
    chunkPointSamplesFromCSV(chunks)


def oclResampleChunks(operation, chunks_to_resample):
    operationSettingsToCSV(operation)
    resampleChunkPointsToCSV(operation, chunks_to_resample)
    # exportModelsToSTL(operation)
    if os.path.isdir(os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib")):
        call([PYTHON_BIN, os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib", "oclSample.py")])
    else:
        call([PYTHON_BIN, os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib", "oclSample.py")])
    chunkPointsResampleFromCSV(chunks_to_resample)


def oclWaterlineLayerHeights(operation):
    layers = []
    l_last = operation.minz
    l_step = operation.stepdown
    l_first = operation.maxz - l_step
    l_depth = l_first
    while l_depth > (l_last + 0.0000001):
        layers.append(l_depth)
        l_depth -= l_step
    layers.append(l_last)
    return layers


def oclWaterlineHeightsToCSV(operation):
    layers = oclWaterlineLayerHeights(operation)
    with open(os.path.join(tempfile.gettempdir(), 'ocl_wl_heights.txt'), 'w') as csv_file:
        for layer in layers:
            csv_file.write("{}\n".format(layer * 1000))


def waterlineChunksFromCSV(operation, chunks):
    layers = oclWaterlineLayerHeights(operation)
    wl_index = 0
    for layer in layers:
        csv_file = open(os.path.join(tempfile.gettempdir(), 'oclWaterline') + str(wl_index) + '.txt', 'r')
        print(str(wl_index) + "\n")
        for line in csv_file:
            if line[0] == 'l':
                chunks.append(camPathChunk(inpoints=[]))
            else:
                point = [float(coord) / OCL_SCALE for coord in line.split()]
                chunks[-1].points.append((point[0], point[1], point[2]))
        wl_index += 1
        csv_file.close()
    chunks.append(camPathChunk(inpoints=[]))


def oclGetMedialAxis(operation, chunks):
    oclWaterlineHeightsToCSV(operation)
    operationSettingsToCSV(operation)
    curvesToCSV(operation)
    call([PYTHON_BIN, os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib", "ocl.py")])
    waterlineChunksFromCSV(operation, chunks)


def oclGetWaterline(operation, chunks):
    oclWaterlineHeightsToCSV(operation)
    operationSettingsToCSV(operation)
    exportModelsToSTL(operation)
    if os.path.isdir(os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib")):
        call([PYTHON_BIN, os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib", "oclWaterline.py")])
    else:
        call([PYTHON_BIN, os.path.join(bpy.utils.script_path_pref(), "addons", "cam", "opencamlib", "oclWaterline.py")])
    waterlineChunksFromCSV(operation, chunks)

# def oclFillMedialAxis(operation):
