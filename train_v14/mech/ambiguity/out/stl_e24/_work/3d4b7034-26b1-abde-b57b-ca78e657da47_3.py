from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
boss_diameter = 40.0
boss_height = 12.0
hole_diameter = 8.0
hole_offset_x = 20.0
hole_offset_y = 15.0
rib_width = 10.0
rib_height = 3.0
chamfer_size = 1.0
pocket_depth = 4.0
pocket_margin = 5.0

base = Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness - boss_height/2) * Cylinder(boss_diameter/2, boss_height)
rib = Pos(0, 0, plate_thickness - rib_height/2) * Box(plate_length - 2 * pocket_margin, rib_width, rib_height)

result = base + boss + rib

hole_positions = [
    (hole_offset_x, hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (-hole_offset_x, -hole_offset_y),
    (hole_offset_x, -hole_offset_y)
]
for x, y in hole_positions:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 10)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

pocket_width = boss_diameter - 2 * pocket_margin
pocket_length = boss_diameter - 2 * pocket_margin
pocket = Pos(0, 0, plate_thickness + boss_height - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
result = result - pocket

part = result
part.name = "plate_with_boss_rib_holes"
export_step(part, "output.step")