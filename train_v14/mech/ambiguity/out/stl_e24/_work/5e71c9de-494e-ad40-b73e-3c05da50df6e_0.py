from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
corner_fillet_radius = 3.0
hole_diameter = 8.0
hole_spacing_x = 30.0
hole_spacing_y = 24.0
pocket_diameter = 30.0
pocket_depth = 6.0
rib_height = 4.0
rib_thickness = 2.0
rib_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = solid_body - Pos(0, 0, plate_thickness) * Cylinder(pocket_diameter/2, pocket_depth)

rib = Pos(0, plate_width/2 - rib_offset, plate_thickness/2) * Box(plate_length - 2*rib_offset, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_rib"
export_step(part, "output.step")