from build123d import *

base_length = 80.0
base_width = 50.0
base_thickness = 10.0
cyl_radius = 20.0
cyl_height = 20.0
cone_height = 30.0
cone_tip_radius = 6.0
hole_diameter = 6.0
hole_offset = 10.0
chamfer_size = 1.0
pocket_length = 20.0
pocket_width = 10.0
pocket_depth = 5.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
cyl = Pos(0, 0, base_thickness + cyl_height/2) * Cylinder(cyl_radius, cyl_height)
cone = Pos(0, 0, base_thickness + cyl_height + cone_height/2) * Cone(cyl_radius, cone_tip_radius, cone_height)

result = base + cyl + cone

bottom_edges = result.edges().sort_by(Axis.Z)[:1]
result = chamfer(bottom_edges, chamfer_size)

hole_positions = [
    (-base_length/2 + hole_offset, -base_width/2 + hole_offset),
    (base_length/2 - hole_offset, -base_width/2 + hole_offset),
    (base_length/2 - hole_offset, base_width/2 - hole_offset),
    (-base_length/2 + hole_offset, base_width/2 - hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, base_thickness/2) * Cylinder(hole_diameter/2, base_thickness)

pocket_z = base_thickness + cyl_height + cone_height - pocket_depth/2
result = result - Pos(0, 0, pocket_z) * Box(pocket_length, pocket_width, pocket_depth)

part = result
part.name = "base_with_cyl_cone_holes_pocket"
export_step(part, "output.step")