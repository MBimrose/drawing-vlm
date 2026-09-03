from build123d import *

tube_length = 80.0
outer_radius = 12.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
slot_width = 4.0
slot_length = 20.0
slot_depth = wall_thickness + 0.5
hole_diameter = 2.0
hole_spacing = 6.0
hole_count = int((tube_length - 20) // hole_spacing)
chamfer_size = 0.5

solid_body = Cylinder(outer_radius, tube_length) - Cylinder(inner_radius, tube_length)

slot_box = Pos(outer_radius - slot_depth/2, 0, -tube_length/2 + slot_length/2) * Box(slot_depth, slot_width, slot_length)
solid_body = solid_body - slot_box

slot_edges = solid_body.edges().filter_by(Axis.X)
solid_body = chamfer(slot_edges, chamfer_size)

for i in range(hole_count):
    z_pos = -tube_length/2 + 10 + i * hole_spacing
    hole = Pos(outer_radius - wall_thickness/2, 0, z_pos) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, wall_thickness + 1)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_tube_with_slot_and_holes"
export_step(part, "output.step")