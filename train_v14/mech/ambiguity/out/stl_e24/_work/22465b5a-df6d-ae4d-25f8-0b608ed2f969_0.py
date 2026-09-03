from build123d import *

outer_radius = 30
wall_thickness = 5
inner_radius = outer_radius - wall_thickness
length = 80
boss_radius = 10
boss_height = 15
boss_center_z = 20
chamfer_size = 2

outer_cyl = Pos(0, 0, length/2) * Cylinder(outer_radius, length)
inner_cyl = Pos(0, 0, length/2) * Cylinder(inner_radius, length)
tube = outer_cyl - inner_cyl

boss = Pos(outer_radius + boss_height/2, 0, boss_center_z - length/2) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)

result = tube + boss

top_face = result.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "tube_with_boss"
export_step(part, "output.step")