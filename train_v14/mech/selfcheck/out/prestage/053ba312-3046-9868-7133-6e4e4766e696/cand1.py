from build123d import *
import math

outer_diameter = 80.0
length = 60.0
wall_thickness = 5.0
rib_thickness = 4.0
rib_height = 6.0
rib_count = 6
vent_slot_width = 12.0
vent_slot_length = 30.0
fillet_radius = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = fillet(top_face.edges() + bottom_face.edges(), fillet_radius)

vent_slot = Pos(0, 0, length / 2.0) * Box(vent_slot_width, vent_slot_length, wall_thickness + 0.2)
solid_body = solid_body - vent_slot

rib = Pos(inner_radius - rib_thickness / 2.0, 0, 0) * Box(rib_thickness, rib_height, length)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")