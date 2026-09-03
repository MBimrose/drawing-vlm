from build123d import *
import math

plate_width = 70.0
plate_height = 40.0
plate_thickness = 8.0
oval_width = 30.0
oval_height = 15.0
oval_depth = 4.0
hole_diameter = 5.0
countersink_diameter = 8.5
countersink_angle = 82.0
chamfer_size = 0.5
rib_width = 10.0
rib_height = 5.0
rib_thickness = 3.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part

with BuildPart() as oval_p:
    with BuildSketch(Plane.XY.offset(plate_thickness)) as oval_s:
        Ellipse(oval_width/2, oval_height/2)
    extrude(amount=-oval_depth)
solid_body = solid_body - oval_p.part

hole_positions = [
    (0, 0),
    (-plate_width/3, -plate_height/3),
    (plate_width/3, -plate_height/3)
]

for x, y in hole_positions:
    csk = CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)
    solid_body = solid_body - Pos(x, y, plate_thickness) * csk

rib = Pos(0, 0, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_oval_pocket_and_holes"
export_step(part, "output.step")