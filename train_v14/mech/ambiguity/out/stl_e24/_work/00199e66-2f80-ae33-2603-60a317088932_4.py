from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 12.0
pocket_diameter = 30.0
pocket_depth = 6.0
hole_diameter = 5.0
countersink_diameter = 10.0
countersink_angle = 82.0
hole_spacing_x = 50.0
hole_spacing_y = 30.0
rib_width = 8.0
rib_height = 4.0
chamfer_size = 1.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)
solid_body = solid_body - pocket

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2),
]
for x, y in hole_positions:
    csk = Pos(x, y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)
    solid_body = solid_body - csk

rib1 = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(plate_length - 20, rib_width, rib_height)
rib2 = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width - 20, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")