from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_height = 2.0
rib_width = 5.0
hole_diameter = 10.0
corner_hole_diameter = 6.0
corner_hole_offset = 10.0
chamfer_distance = 0.5
reinforcement_rib_width = 8.0
reinforcement_rib_height = 3.0
reinforcement_rib_length = 30.0

base = Box(plate_length, plate_width, plate_thickness)
rib_outer = Box(plate_length + 2 * rib_width, plate_width + 2 * rib_width, rib_height)
rib_inner = Box(plate_length, plate_width, rib_height)
rib = rib_outer - rib_inner
result = base + rib

result = result - Cylinder(hole_diameter / 2, plate_thickness + rib_height + 10)

corner_x = plate_length / 2 - corner_hole_offset
corner_y = plate_width / 2 - corner_hole_offset
for x, y in [(corner_x, corner_y), (-corner_x, corner_y), (corner_x, -corner_y), (-corner_x, -corner_y)]:
    result = result - Pos(x, y, 0) * Cylinder(corner_hole_diameter / 2, plate_thickness + rib_height + 10)

result = chamfer(result.edges(), chamfer_distance)

reinforcement = Pos(0, 0, -plate_thickness / 2 + reinforcement_rib_height / 2) * Box(reinforcement_rib_length, reinforcement_rib_width, reinforcement_rib_height)
result = result + reinforcement

part = result
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")