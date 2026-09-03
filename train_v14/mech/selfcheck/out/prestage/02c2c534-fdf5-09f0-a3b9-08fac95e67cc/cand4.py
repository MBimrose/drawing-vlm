from build123d import *
import math

shaft_diameter = 20.0
shaft_length = 70.0
shoulder_diameter = 30.0
shoulder_length = 10.0
groove_width = 5.0
groove_depth = 2.0
groove_spacing = 12.0
groove_count = 4
chamfer_size = 0.5
hole_diameter = 4.0

shaft_radius = shaft_diameter / 2.0
shoulder_radius = shoulder_diameter / 2.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(shaft_radius)
    with BuildSketch(Plane.XY.offset(shaft_length)) as s2:
        Circle(shaft_radius)
    loft()
shaft_body = p.part

shoulder_body = Pos(0, 0, shoulder_length / 2) * Cylinder(shoulder_radius, shoulder_length)
base = shaft_body + shoulder_body

for i in range(groove_count):
    z_pos = shoulder_length + i * groove_spacing
    angle = i * 30
    groove = Pos(0, 0, z_pos) * Rot(0, 0, angle) * Pos(shaft_radius - groove_depth / 2.0, 0, shaft_length / 2.0) * Box(groove_width, groove_depth, shaft_length)
    base = base - groove

hole = Pos(0, 0, (shaft_length + shoulder_length) / 2) * Cylinder(hole_diameter / 2, shaft_length + shoulder_length)
base = base - hole

part = base
part.name = "shaft_with_grooves"
export_step(part, "output.step")