from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
cutout_width = 40.0
cutout_height = 30.0
cutout_fillet_radius = 2.0
hole_diameter = 5.0
hole_counterbore_diameter = 8.0
hole_counterbore_depth = 2.0
rib_thickness = 3.0
rib_height = 4.0
rib_offset = 5.0
hole_offset_x = 22.5
hole_offset_y = 22.5

result = Box(plate_length, plate_width, plate_thickness)

cutout_body = Box(cutout_width, cutout_height, plate_thickness)
cutout_edges = cutout_body.edges().filter_by(Axis.Z)
cutout_body = fillet(cutout_edges, cutout_fillet_radius)
result = result - cutout_body

for x, y in [(-hole_offset_x, hole_offset_y), (hole_offset_x, hole_offset_y), (0, -hole_offset_y)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)
    result = result - Pos(x, y, plate_thickness/2 - hole_counterbore_depth/2) * Cylinder(hole_counterbore_diameter/4, hole_counterbore_depth)

rib_length = plate_length - 2 * rib_offset
rib1 = Pos(0, plate_width/4, -plate_thickness/2 - rib_height/2) * Box(rib_length, rib_thickness, rib_height)
rib2 = Pos(0, -plate_width/4, -plate_thickness/2 - rib_height/2) * Box(rib_length, rib_thickness, rib_height)
result = result + rib1 + rib2

part = result
part.name = "plate_with_cutout_holes_and_ribs"
export_step(part, "output.step")