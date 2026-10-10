from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 10.0
boss_radius = 20.0
boss_height = 20.0
cone_height = 30.0
cone_top_radius = 5.0
hole_diameter = 6.0
hole_offset = 10.0
chamfer_size = 1.0
pocket_length = 20.0
pocket_width = 10.0
pocket_depth = 5.0

base = Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
cone = Pos(0, 0, plate_thickness/2 + boss_height + cone_height/2) * Cone(boss_radius, cone_top_radius, cone_height)

result = base + boss + cone

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

pocket = Pos(0, 0, plate_thickness/2 + boss_height + cone_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

part = result
part.name = "plate_with_boss_cone"
export_step(part, "output.step")