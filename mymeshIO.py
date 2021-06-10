import re
import pymesh
import numpy as np
from pyproj import CRS
from pyproj import Transformer


# read mesh string into vertices and faces
def read_mesh(phs, tol):
    surfaces = phs.split(")),((")
    for index, surface in enumerate(surfaces):
        tempsurf = np.array(re.findall(r'[-]*[\d]+[\.]*[\d]*', surface), dtype="float")
        if len(tempsurf) != 0:
            surfaces[index] = np.split(tempsurf, int(len(tempsurf) / 3))
            del surfaces[index][-1]
    flat = []
    for surface in surfaces:
        for vert in surface:
            vert[-1] = vert[-1] / 10000
            flat.append(vert)
    vertices = np.unique(flat, axis=0)
    faces = []
    for index, surface in enumerate(surfaces):
        faces.append([])
        for vert in surface:
            faces[index].append([np.array_equal(vert, x) for x in vertices].index(True))
    return np.round(vertices, tol), np.array(faces)


def read_in_pymesh(data, tol):
    mesh = read_mesh(data, tol)
    return pymesh.form_mesh(mesh[0], mesh[1])


# format and write pymesh into mesh string
def write_mesh(mesh):
    output = "POLYHEDRALSURFACE Z ("
    for face in mesh.faces:
        output += "(("
        for index in face:
            coord = mesh.vertices[index]
            output += f"{coord[0]:.8f} {coord[1]:.8f} {coord[2] * 10000:.2f},"
        coord = mesh.vertices[face[0]]
        output += f"{coord[0]:.8f} {coord[1]:.8f} {coord[2] * 10000:.2f})),"
    output = output[:-1] + ")"
    if output == ")":
        output = "empty"
    return output


# calculate zone for pcs conversion
def calc_zone(vertex):
    if vertex[1] > 0:
        pref = 32600
    else:
        pref = 32700
    zone = int((vertex[0] + 180) / 6) + 1
    return zone + pref


# transform pymesh object to pcs coordinate system
def transform_mesh_to_pcs(input, tol=8):
    if input == "empty":
        return 0
    elif type(input) == str:
        mesh = read_in_pymesh(input, tol)
    elif input.num_faces == 0:
        return input
    else:
        mesh = input
    zone = calc_zone(mesh.vertices[0])
    crs = CRS.from_epsg(zone)
    proj = Transformer.from_crs(crs.geodetic_crs, crs)
    vertices = np.transpose(mesh.vertices)
    vertices = proj.transform(vertices[1], vertices[0], vertices[2] * 10000)
    outmesh = pymesh.form_mesh(np.transpose(vertices), mesh.faces)
    return outmesh
