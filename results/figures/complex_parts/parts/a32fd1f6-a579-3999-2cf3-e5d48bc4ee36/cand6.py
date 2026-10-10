from build123d import *

base_length = 80.0
base_width = 50.0
base_thickness = 10.0
boss_radius = 20.0
boss_height = 20.0
cone_height = 30.0
cone_top_radius = 6.0
hole_diameter = 6.0
hole_offset = 10.0
chamfer_size = 1.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
boss = Pos(0, 0, base_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
cone = Pos(0, 0, base_thickness + boss_height + cone_height/2) * Cone(boss_radius, cone_top_radius, cone_height)

solid_body = base + boss + cone

hole_positions = [
    (-base_length/2 + hole_offset, -base_width/2 + hole_offset),
    ( base_length/2 - hole_offset, -base_width/2 + hole_offset),
    ( base_length/2 - hole_offset,  base_width/2 - hole_offset),
    (-base_length/2 + hole_offset,  base_width/2 - hole_offset),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, 200)

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "base_with_boss_cone_and_holes"
export_step(part, "output.step")