from build123d import *

enclosure_length = 80.0
enclosure_width = 50.0
enclosure_height = 30.0
wall_thickness = 2.0
pocket_length = 60.0
pocket_width = 30.0
pocket_depth = 10.0
mount_hole_diameter = 4.0
mount_hole_offset = 15.0

base = Pos(0, 0, enclosure_height / 2) * Box(enclosure_length, enclosure_width, enclosure_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, 0, enclosure_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

hole = Pos(enclosure_length / 2, 0, enclosure_height / 2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, enclosure_length)
base = base - hole

part = base
part.name = "enclosure"
export_step(part, "output.step")