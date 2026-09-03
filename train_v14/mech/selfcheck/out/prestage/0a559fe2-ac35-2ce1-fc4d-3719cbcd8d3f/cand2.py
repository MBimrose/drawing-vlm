from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_spacing = 20.0
chamfer_size = 1.0
mount_hole_diameter = 3.0
mount_hole_spacing = 20.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness

rib_count = int((inner_length - rib_spacing) // rib_spacing) + 1
rib_positions = [(-inner_length/2 + rib_spacing/2 + i * rib_spacing) for i in range(rib_count)]

result = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

cavity = Pos(0, 0, inner_height/2) * Box(inner_length, inner_width, inner_height)
result = result - cavity

for x in rib_positions:
    rib = Pos(x, 0, wall_thickness + inner_height/2) * Box(rib_thickness, inner_width, inner_height)
    result = result + rib

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(outer_length/2, y, outer_height/2 + outer_height/4) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length)
    result = result - hole

front_face = result.faces().sort_by(Axis.Y)[-1]
result = chamfer(front_face.edges(), chamfer_size)

part = result
part.name = "hollow_box_with_ribs"
export_step(part, "output.step")