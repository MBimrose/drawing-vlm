from build123d import *
import math

outer_diameter = 80.0
height = 50.0
wall_thickness = 6.0
rib_thickness = 4.0
rib_width = 12.0
rib_count = 12
central_hole_diameter = 20.0
slot_width = 30.0
slot_depth = 10.0
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Cylinder(central_hole_diameter / 2, height)

slot_box = Pos(0, 0, height - slot_depth / 2) * Box(slot_width, slot_depth, slot_depth)
solid_body = solid_body - slot_box

rib = Pos(inner_radius - rib_thickness / 2.0, 0, height / 2.0) * Box(rib_thickness, rib_width, height)
ribs = rib
for i in range(1, rib_count):
    angle = 360.0 / rib_count * i
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")