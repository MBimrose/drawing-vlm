from build123d import *
import math

plate_width = 70.0
plate_height = 40.0
plate_thickness = 8.0
oval_width = 25.0
oval_height = 12.0
oval_depth = 4.0
hole_diameter = 5.0
countersink_diameter = 8.5
countersink_angle = 82.0
chamfer_size = 0.5
rib_width = 10.0
rib_height = 5.0
rib_thickness = 2.0

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

with BuildPart() as oval_bp:
    with BuildSketch(Plane.XY.offset(plate_thickness/2)) as oval_sk:
        Ellipse(oval_width/2, oval_height/2)
    extrude(amount=-oval_depth)
solid_body = solid_body - oval_bp.part

rib = Pos(0, 0, -plate_thickness/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

hole_positions = [
    (-plate_width/3, -plate_height/3),
    (plate_width/3, -plate_height/3),
    (0, plate_height/3)
]
for x, y in hole_positions:
    csk = Pos(x, y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)
    solid_body = solid_body - csk

part = solid_body
part.name = "plate_with_oval_pocket_rib_and_holes"
export_step(part, "output.step")