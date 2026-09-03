from build123d import *

enclosure_length = 80.0
enclosure_width = 50.0
enclosure_height = 30.0
wall_thickness = 2.0
base_thickness = 3.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 10.0
mount_hole_diameter = 2.0
mount_hole_offset = 5.0
chamfer_size = 0.5

total_height = base_thickness + enclosure_height

solid_body = Pos(0, 0, total_height / 2) * Box(enclosure_length, enclosure_width, total_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, 0, total_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole_positions = [
    (-enclosure_length / 2 + mount_hole_offset, -enclosure_width / 2 + mount_hole_offset),
    (enclosure_length / 2 - mount_hole_offset, -enclosure_width / 2 + mount_hole_offset),
    (-enclosure_length / 2 + mount_hole_offset, enclosure_width / 2 - mount_hole_offset),
    (enclosure_length / 2 - mount_hole_offset, enclosure_width / 2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, total_height / 2) * Cylinder(mount_hole_diameter / 2, total_height + 10)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "enclosure"
export_step(part, "output.step")