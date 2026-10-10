from build123d import *

outer_diameter = 80.0
wall_thickness = 4.0
length = 20.0
central_hole_diameter = 8.0
slot_width = 6.0
slot_length = 12.0
chamfer_size = 1.0
rib_thickness = 2.0
rib_width = 8.0
rib_count = 4

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Rot(0, 90, 0) * Cylinder(outer_radius, length)
solid_body = solid_body - Rot(0, 90, 0) * Cylinder(inner_radius, length)
solid_body = solid_body - Rot(0, 90, 0) * Cylinder(central_hole_diameter / 2.0, length)

slot_box = Pos(0, outer_radius - wall_thickness / 2.0, 0) * Box(length, slot_width, slot_length)
solid_body = solid_body - slot_box

rib = Pos(inner_radius - rib_thickness / 2.0, 0, 0) * Box(rib_thickness, rib_width, length)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(angle, 0, 0) * rib

solid_body = solid_body + ribs
solid_body = chamfer(solid_body.edges().filter_by(Axis.X), chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")