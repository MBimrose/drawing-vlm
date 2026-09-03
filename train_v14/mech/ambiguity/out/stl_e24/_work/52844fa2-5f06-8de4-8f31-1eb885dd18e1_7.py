from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_length = 40.0
pocket_width = 30.0
pocket_fillet_radius = 2.0
hole_diameter = 5.0
hole_offset = 15.0
rib_height = 4.0
rib_width = 3.0
rib_length = 60.0
rib_spacing = 40.0
cbore_diameter = 6.0
cbore_depth = 2.0

solid_body = Box(plate_length, plate_width, plate_thickness)

pocket = Box(pocket_length, pocket_width, plate_thickness)
pocket = fillet(pocket.edges().filter_by(Axis.Z), pocket_fillet_radius)
solid_body = solid_body - pocket

hole_positions = [
    (-hole_offset, plate_width/2 - hole_offset),
    (hole_offset, plate_width/2 - hole_offset),
    (0, -plate_width/2 + hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)
    solid_body = solid_body - Pos(x, y, plate_thickness/2 - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)

for y in [-rib_spacing/2, rib_spacing/2]:
    rib = Pos(0, y, -plate_thickness/2 - rib_height/2) * Box(rib_length, rib_width, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")