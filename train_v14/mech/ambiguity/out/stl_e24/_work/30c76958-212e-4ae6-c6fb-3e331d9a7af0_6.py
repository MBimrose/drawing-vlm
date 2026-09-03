from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 12.0
wall_thickness = 4.0
latch_tab_width = 20.0
latch_tab_height = 6.0
latch_tab_thickness = 2.0
rib_thickness = 2.0
rib_height = 3.0
rib_spacing = 15.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
chamfer_size = 0.5

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness

base = Box(outer_length, outer_width, outer_height)
cavity = Pos(0, 0, -wall_thickness / 2) * Box(inner_length, inner_width, inner_height)
result = base - cavity

latch = Pos(0, outer_width / 2 + latch_tab_thickness / 2, 0) * Box(latch_tab_width, latch_tab_thickness, latch_tab_height)
result = result + latch

rib_count = int((inner_width - rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    y_pos = -inner_width / 2 + rib_spacing / 2 + i * rib_spacing
    rib = Pos(0, y_pos, -wall_thickness / 2) * Box(inner_length, rib_thickness, rib_height)
    result = result + rib

hole_positions = [
    (-outer_length / 2 + mount_hole_offset, -outer_width / 2 + mount_hole_offset),
    (outer_length / 2 - mount_hole_offset, -outer_width / 2 + mount_hole_offset),
    (-outer_length / 2 + mount_hole_offset, outer_width / 2 - mount_hole_offset),
    (outer_length / 2 - mount_hole_offset, outer_width / 2 - mount_hole_offset),
]
for x, y in hole_positions:
    hole = Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, outer_height)
    result = result - hole

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "box_with_cavity_latch_ribs"
export_step(part, "output.step")