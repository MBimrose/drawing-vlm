from build123d import *

outer_diameter = 80.0
inner_diameter = 60.0
length = 70.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 5.0
boss_width = 20.0
boss_height = 10.0
boss_thickness = 5.0
chamfer_size = 1.0
hole_diameter = 5.0
hole_offset = 30.0
keyway_width = 10.0
keyway_length = 15.0
keyway_offset = 30.0

solid_body = Cylinder(outer_diameter / 2.0, length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket = Pos(outer_diameter / 2.0 - pocket_depth / 2.0, 0, length / 2.0) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

boss = Pos(inner_diameter / 2.0 + boss_thickness / 2.0, 0, boss_height / 2.0) * Box(boss_width, boss_thickness, boss_height)
solid_body = solid_body + boss

hole = Pos(hole_offset, 0, length / 2.0) * Cylinder(hole_diameter / 2.0, length)
solid_body = solid_body - hole

keyway = Pos(keyway_offset, 0, length / 2.0) * Box(keyway_width, keyway_length, length)
solid_body = solid_body - keyway

part = solid_body
part.name = "hollow_cylinder_with_features"
export_step(part, "output.step")