from build123d import *

outer_diameter = 40.0
wall_thickness = 3.0
length = 100.0
slot_width = 1.5
slot_length = 30.0
slot_offset = 30.0
hole_diameter = 2.0
hole_spacing = 15.0
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

tube = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

slot_box = Pos(outer_radius - wall_thickness / 2.0, 0, slot_offset) * Box(wall_thickness + 0.2, slot_width, slot_length)
tube = tube - slot_box

for i in range(2):
    for j in range(2):
        x = (i - 0.5) * hole_spacing
        y = (j - 0.5) * hole_spacing
        hole = Pos(outer_radius - wall_thickness / 2.0, x, slot_offset + y) * Cylinder(hole_diameter / 2.0, wall_thickness + 0.5)
        tube = tube - hole

z_edges = tube.edges().filter_by(Axis.Z)
tube = chamfer(z_edges, chamfer_size)

part = tube
part.name = "tube_with_slot_and_holes"
export_step(part, "output.step")