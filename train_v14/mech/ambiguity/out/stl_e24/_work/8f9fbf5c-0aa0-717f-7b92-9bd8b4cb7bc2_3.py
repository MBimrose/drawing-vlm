from build123d import *
import math

bracket_length = 70.0
bracket_width = 40.0
bracket_thickness = 8.0
oval_width = 20.0
oval_height = 12.0
oval_depth = 4.0
hole_diameter = 5.0
countersink_diameter = 8.5
countersink_angle = 82.0
hole_spacing = 20.0
rib_width = 6.0
rib_height = 4.0
rib_thickness = 2.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part

with BuildPart() as oval_p:
    with BuildSketch(Plane.XY.offset(bracket_thickness)) as oval_s:
        Ellipse(oval_width/2, oval_height/2)
    extrude(amount=-oval_depth)

solid_body = solid_body - oval_p.part

hole_positions = [
    (-bracket_length/2 + hole_spacing/2, -bracket_width/2 + hole_spacing/2),
    (bracket_length/2 - hole_spacing/2, -bracket_width/2 + hole_spacing/2),
    (0, bracket_width/2 - hole_spacing/2)
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, bracket_thickness) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, bracket_thickness, countersink_angle)

rib = Pos(0, 0, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")