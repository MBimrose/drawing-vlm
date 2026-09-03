from build123d import *

base_width = 80.0
base_depth = 60.0
base_thickness = 6.0
boss_radius = 8.0
boss_height = 12.0
hole_diameter = 3.2
hole_offset = 10.0
chamfer_size = 0.8
rib_width = 10.0
rib_height = 4.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_cut_depth = 2.0

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_depth, base_thickness)
boss = Pos(0, 0, boss_height/2) * Cylinder(boss_radius, boss_height)
rib = Pos(0, base_depth/2 - rib_width/2, base_thickness/2) * Box(rib_width, rib_height, base_thickness)

result = base + boss + rib

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

hole_positions = [
    (hole_offset, hole_offset),
    (base_width - hole_offset, hole_offset),
    (hole_offset, base_depth - hole_offset),
    (base_width - hole_offset, base_depth - hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

pocket = Pos(0, 0, boss_height - pocket_cut_depth/2) * Box(pocket_width, pocket_depth, pocket_cut_depth)
result = result - pocket

part = result
part.name = "base_plate_with_boss"
export_step(part, "output.step")