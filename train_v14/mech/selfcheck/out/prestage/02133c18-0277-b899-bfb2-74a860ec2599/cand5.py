from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_height = 3.0
rib_width = 5.0
central_hole_diameter = 10.0
corner_hole_diameter = 6.0
corner_hole_offset = 10.0
chamfer_size = 0.5

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
rib_outer = Pos(0, 0, rib_height/2) * Box(plate_length + 2*rib_width, plate_width + 2*rib_width, rib_height)
rib_inner = Pos(0, 0, rib_height/2) * Box(plate_length, plate_width, rib_height)
rib = rib_outer - rib_inner
internal_rib = Pos(0, 0, rib_height/2) * Box(plate_length - 20, rib_width, rib_height)

result = base + rib + internal_rib

hole_height = plate_thickness + rib_height + 10
result = result - Pos(0, 0, plate_thickness/2) * Cylinder(central_hole_diameter/2, hole_height)

corner_points = [
    (-plate_length/2 + corner_hole_offset, -plate_width/2 + corner_hole_offset),
    ( plate_length/2 - corner_hole_offset, -plate_width/2 + corner_hole_offset),
    (-plate_length/2 + corner_hole_offset,  plate_width/2 - corner_hole_offset),
    ( plate_length/2 - corner_hole_offset,  plate_width/2 - corner_hole_offset),
]
for x, y in corner_points:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(corner_hole_diameter/2, hole_height)

result = chamfer(result.edges(), chamfer_size)

part = result
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")