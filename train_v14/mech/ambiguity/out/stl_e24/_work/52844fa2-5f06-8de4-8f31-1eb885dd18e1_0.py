from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 4.0
pocket_fillet_radius = 2.0
hole_diameter = 5.0
hole_counterbore_diameter = 8.0
hole_counterbore_depth = 2.0
hole_offset = 15.0
rib_thickness = 3.0
rib_height = 4.0
rib_spacing = 30.0

result = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
pocket = fillet(pocket.edges().filter_by(Axis.Z), pocket_fillet_radius)
result = result - pocket

hole_positions = [
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
    (0, -plate_width/2 + hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)
    result = result - Pos(x, y, plate_thickness/2 - hole_counterbore_depth/2) * Cylinder(hole_counterbore_diameter/4, hole_counterbore_depth)

rib_length = plate_length - 2*hole_offset
rib1 = Pos(0, -rib_spacing/2, -plate_thickness/2 - rib_height/2) * Box(rib_length, rib_thickness, rib_height)
rib2 = Pos(0, rib_spacing/2, -plate_thickness/2 - rib_height/2) * Box(rib_length, rib_thickness, rib_height)
result = result + rib1 + rib2

part = result
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")