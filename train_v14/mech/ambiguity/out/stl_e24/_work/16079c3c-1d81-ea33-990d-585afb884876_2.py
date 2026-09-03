from build123d import *

length = 80.0
width = 30.0
thickness = 6.0
boss_diameter = 12.0
boss_height = 4.0
hole_diameter = 4.0
hole_spacing = 15.0
num_holes = 4
fillet_radius = 1.0
chamfer_distance = 0.7

solid_body = Pos(0, 0, length/2) * Box(width, thickness, length)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

boss = Pos(0, thickness/2, 0) * Rot(90, 0, 0) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

for i in range(num_holes):
    x = (i - (num_holes - 1) / 2) * hole_spacing
    hole = Pos(x, 0, length/2) * Cylinder(hole_diameter/2, length + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")