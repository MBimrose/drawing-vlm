from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 6.0
height = 55.0
rib_thickness = 2.0
rib_height = 12.0
rib_count = 12
pocket_diameter = 30.0
pocket_depth = 8.0
chamfer_size = 1.5

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

pocket = Pos(0, 0, height - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)
solid_body = solid_body - pocket

rib = Pos(inner_radius - rib_thickness/2, 0, height/2) * Box(rib_thickness, rib_height, height)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

part = solid_body + ribs
part.name = "XMountSocket"
export_step(part, "output.step")