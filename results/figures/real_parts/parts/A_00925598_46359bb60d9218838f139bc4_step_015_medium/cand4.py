from build123d import *

plate_width = 80.0
plate_depth = 80.0
plate_thickness = 15.0
boss_radius = 30.0
boss_height = 60.0
hole_radius = 5.0
hole_offset = 10.0
chamfer_size = 5.0
boss_chamfer = 1.0

plate = Box(plate_width, plate_depth, plate_thickness)
boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
result = plate + boss

inner_hole = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius/2, boss_height + plate_thickness + 10)
result = result - inner_hole

hole_positions = [
    (plate_width/2 - hole_offset, plate_depth/2 - hole_offset),
    (-plate_width/2 + hole_offset, plate_depth/2 - hole_offset),
    (-plate_width/2 + hole_offset, -plate_depth/2 + hole_offset),
    (plate_width/2 - hole_offset, -plate_depth/2 + hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_radius, plate_thickness + 10)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)
result = chamfer(result.edges(), boss_chamfer)

part = result
part.name = "plate_with_boss"
export_step(part, "output.step")