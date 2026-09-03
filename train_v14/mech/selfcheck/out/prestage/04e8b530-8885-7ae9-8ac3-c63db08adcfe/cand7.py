from build123d import *
import math

outer_diameter = 80
cap_height = 30
wall_thickness = 5
rib_height = 20
rib_thickness = 2
rib_width = 3
rib_count = 8
vent_hole_diameter = 5
vent_hole_count = 12
vent_hole_radius = 30
chamfer_size = 1
fillet_radius = 2

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, cap_height) - Cylinder(inner_radius, cap_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = fillet(bottom_face.edges(), fillet_radius)

rib = Pos(inner_radius - rib_thickness/2, 0, cap_height/2) * Box(rib_thickness, rib_width, rib_height)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

for i in range(vent_hole_count):
    angle = i * 360.0 / vent_hole_count
    x = vent_hole_radius * math.cos(math.radians(angle))
    y = vent_hole_radius * math.sin(math.radians(angle))
    solid_body = solid_body - Pos(x, y, cap_height/2) * Cylinder(vent_hole_diameter/2, cap_height)

part = solid_body
part.name = "cap_with_ribs_and_vents"
export_step(part, "output.step")