from build123d import *

plate_length = 60
plate_width = 40
plate_thickness = 15
tab_length = 20
tab_width = 12
hole_diameter = 8
hole_spacing = 30
rib_height = 3
rib_thickness = 2
rib_length = plate_length - 10

base_plate = Box(plate_length, plate_width, plate_thickness)
tab = Pos(plate_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, plate_thickness)
solid_body = base_plate + tab

hole_positions = [
    (-hole_spacing/2, -hole_spacing/2),
    ( hole_spacing/2, -hole_spacing/2),
    (-hole_spacing/2,  hole_spacing/2),
    ( hole_spacing/2,  hole_spacing/2)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

rib = Pos(0, 0, plate_thickness/2) * Box(rib_length, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_tab_holes_and_rib"
export_step(part, "output.step")