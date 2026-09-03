from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_count = 3
chamfer_size = 1.0
mount_hole_diameter = 3.0
mount_hole_spacing = 20.0
mount_hole_offset = 10.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness
rib_height = inner_height - wall_thickness
rib_spacing = (inner_length - rib_count * rib_thickness) / (rib_count + 1)

solid_body = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

rib_positions = [
    -inner_length / 2 + rib_spacing + rib_thickness / 2 + i * (rib_spacing + rib_thickness)
    for i in range(rib_count)
]
for x in rib_positions:
    rib = Pos(x, 0, wall_thickness + rib_height / 2) * Box(rib_thickness, inner_width, rib_height)
    solid_body = solid_body + rib

for y in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    hole = Pos(outer_length / 2, y, outer_height / 2 + mount_hole_offset) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, outer_length)
    solid_body = solid_body - hole

front_face = solid_body.faces().sort_by(Axis.Y)[-1]
front_edges = front_face.edges()
solid_body = chamfer(front_edges, chamfer_size)

part = solid_body
part.name = "hollow_box_with_ribs"
export_step(part, "output.step")