from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
front_chamfer = 1.0
mount_hole_diameter = 3.0
mount_hole_spacing = 20.0
mount_hole_offset_z = 10.0
rib_thickness = 2.0
rib_count = 3

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness
rib_height = inner_height - wall_thickness
rib_spacing = inner_length / (rib_count + 1)

outer_box = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
inner_box = Pos(0, 0, inner_height / 2) * Box(inner_length, inner_width, inner_height)
result = outer_box - inner_box

front_face = result.faces().sort_by(Axis.Y)[-1]
result = chamfer(front_face.edges(), front_chamfer)

hole_r = mount_hole_diameter / 2
hole_tool = Rot(0, 90, 0) * Cylinder(hole_r, outer_length + 10)
for y, z in [(-mount_hole_spacing / 2, mount_hole_offset_z), (mount_hole_spacing / 2, mount_hole_offset_z)]:
    result = result - Pos(outer_length / 2, y, z) * hole_tool

for i in range(rib_count):
    x = -inner_length / 2 + rib_spacing * (i + 1)
    rib = Pos(x, 0, wall_thickness + rib_height / 2) * Box(rib_thickness, inner_width, rib_height)
    result = result + rib

part = result
part.name = "hollow_box_with_ribs"
export_step(part, "output.step")