from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
cutout_length = 40.0
cutout_width = 30.0
hole_diameter = 4.0
hole_depth = 6.0
hole_spacing_x = 20.0
hole_spacing_y = 30.0
fillet_radius = 2.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = chamfer(solid_body.edges(), chamfer_distance)

cutout = Pos(0, 0, plate_thickness/2) * Box(cutout_length, cutout_width, plate_thickness)
solid_body = solid_body - cutout

hole_positions = [
    (-hole_spacing_x, -hole_spacing_y/2),
    (0, -hole_spacing_y/2),
    (hole_spacing_x, -hole_spacing_y/2),
    (-hole_spacing_x, hole_spacing_y/2),
    (0, hole_spacing_y/2),
    (hole_spacing_x, hole_spacing_y/2),
]

for x, y in hole_positions:
    hole = Pos(x, y, plate_thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_cutout_and_holes"
export_step(part, "output.step")