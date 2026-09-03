from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
corner_fillet_radius = 3.0
central_recess_diameter = 30.0
central_recess_depth = 2.0
hole_diameter = 8.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
rib_width = 10.0
rib_length = 40.0
rib_depth = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

solid_body = solid_body - Pos(0, 0, plate_thickness - central_recess_depth/2) * Cylinder(central_recess_diameter/2, central_recess_depth)

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = solid_body - Pos(0, 0, plate_thickness - rib_depth/2) * Box(rib_length, rib_width, rib_depth)

part = solid_body
part.name = "plate_with_recess_holes_and_rib"
export_step(part, "output.step")