from build123d import *

plate_width = 80.0
plate_height = 80.0
plate_thickness = 10.0
frame_width = 20.0
hole_diameter = 5.0
hole_offset = 10.0
chamfer_size = 0.5
boss_radius = 10.0
boss_height = 5.0

inner_width = plate_width - 2 * frame_width
inner_height = plate_height - 2 * frame_width
half_inner_w = inner_width / 2.0
half_inner_h = inner_height / 2.0
hole_r = hole_diameter / 2.0

hole_positions = [
    (-plate_width/2 + hole_offset, -plate_height/2 + hole_offset),
    ( plate_width/2 - hole_offset, -plate_height/2 + hole_offset),
    (-plate_width/2 + hole_offset,  plate_height/2 - hole_offset),
    ( plate_width/2 - hole_offset,  plate_height/2 - hole_offset),
    (0, -plate_height/2 + hole_offset),
    (0,  plate_height/2 - hole_offset),
    (-plate_width/2 + hole_offset, 0),
    ( plate_width/2 - hole_offset, 0),
]

base = Box(plate_width, plate_height, plate_thickness)
boss = Cylinder(boss_radius, boss_height)
result = base + boss

pocket = Box(inner_width, inner_height, plate_thickness + boss_height)
result = result - pocket

for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_r, plate_thickness + boss_height)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")