from build123d import *

outer_diameter = 40.0
wall_thickness = 3.0
length = 100.0
slot_width = 6.0
slot_length = 30.0
slot_chamfer = 0.5
hole_diameter = 1.5
hole_count = 5
hole_spacing = 4.0
hole_offset_from_end = 10.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

slot_box = Pos(outer_radius - wall_thickness / 2.0, 0, 0) * Box(slot_width, wall_thickness, slot_length)
slot_box = chamfer(slot_box.edges(), slot_chamfer)
solid_body = solid_body - slot_box

for i in range(hole_count):
    z_pos = hole_offset_from_end + i * hole_spacing
    hole = Pos(outer_radius - wall_thickness / 2.0, 0, z_pos) * Cylinder(hole_diameter / 2.0, wall_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "tube_with_slot_and_holes"
export_step(part, "output.step")