from build123d import *
import math

width = 70.0
depth = 30.0
thickness = 5.0
pocket_width = 30.0
pocket_depth = 15.0
pocket_depth_cut = 2.0
hole_diameter = 3.0
countersink_diameter = 5.0
countersink_angle = 82.0
hole_spacing = 20.0
chamfer_size = 0.5

solid_body = Box(width, depth, thickness)
solid_body = solid_body - Pos(0, 0, thickness/2 - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)

shaft_radius = hole_diameter / 2
csink_radius = countersink_diameter / 2
csink_height = (csink_radius - shaft_radius) / math.tan(math.radians(countersink_angle / 2))

for x in [-hole_spacing, 0, hole_spacing]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(shaft_radius, thickness)
    solid_body = solid_body - Pos(x, 0, thickness/2 - csink_height/2) * Cone(shaft_radius, csink_radius, csink_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_pocket_and_holes"
export_step(part, "output.step")