from build123d import *

outer_radius = 30.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
body_length = 80.0
boss_radius = 10.0
boss_height = 20.0
boss_offset_from_bottom = 10.0
chamfer_size = 2.0

outer_cyl = Pos(0, 0, body_length / 2) * Cylinder(outer_radius, body_length)
inner_cyl = Pos(0, 0, body_length / 2) * Cylinder(inner_radius, body_length)
body = outer_cyl - inner_cyl

boss = Pos(outer_radius + boss_radius, 0, boss_offset_from_bottom) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
combined = body + boss

top_face = combined.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "hollow_cylinder_with_boss"
export_step(part, "output.step")