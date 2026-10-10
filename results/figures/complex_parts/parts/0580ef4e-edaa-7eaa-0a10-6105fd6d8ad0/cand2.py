from build123d import *

outer_radius = 35.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
height = 80.0
chamfer_size = 2.0
rib_width = 4.0
rib_height = 12.0
rib_count = 6
pocket_width = 12.0
pocket_height = 8.0
pocket_depth = wall_thickness

import math

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_width/2, 0, 0) * Box(rib_width, rib_height, height)
    solid_body = solid_body + rib

pocket = Pos(outer_radius - pocket_depth/2, 0, 0) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "hollow_cylinder_with_ribs_and_pocket"
export_step(part, "output.step")