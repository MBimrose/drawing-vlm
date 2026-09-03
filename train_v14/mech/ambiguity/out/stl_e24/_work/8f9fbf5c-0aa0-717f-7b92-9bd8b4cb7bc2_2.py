from build123d import *
import math

plate_width = 70.0
plate_height = 40.0
plate_thickness = 8.0
pocket_major = 20.0
pocket_minor = 12.0
pocket_depth = 4.0
hole_diameter = 5.0
countersink_diameter = 8.5
countersink_angle = 82.0
hole_spacing = 35.0
rib_width = 6.0
rib_length = 20.0
rib_height = 2.0
chamfer_size = 0.5

solid_body = Box(plate_width, plate_height, plate_thickness)

with BuildPart() as pocket_bp:
    with BuildSketch(Plane.XY.offset(plate_thickness/2)) as ps:
        Ellipse(pocket_major/2, pocket_minor/2)
    extrude(amount=-pocket_depth)
solid_body = solid_body - pocket_bp.part

hole_positions = [
    (-hole_spacing/2, -hole_spacing/(2*3**0.5)),
    (hole_spacing/2, -hole_spacing/(2*3**0.5)),
    (0, hole_spacing/(3**0.5))
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)

rib = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_pocket_holes_and_rib"
export_step(part, "output.step")