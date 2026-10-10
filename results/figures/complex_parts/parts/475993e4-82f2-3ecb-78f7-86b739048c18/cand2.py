from build123d import *

base_width = 80.0
base_depth = 40.0
knob_height = 30.0
top_radius = 15.0
rib_width = 8.0
rib_height = 15.0
rib_length = 20.0
hole_diameter = 10.0
hole_depth = knob_height - 4.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Rectangle(base_width, base_depth)
    with BuildSketch(Plane.XY.offset(knob_height)) as s2:
        Circle(top_radius)
    loft()

solid_body = p.part

rib = Box(rib_length, rib_width, rib_height)
rib_left = Pos(-base_width/2 + rib_length/2, 0, rib_height/2) * rib
rib_right = Pos(base_width/2 - rib_length/2, 0, rib_height/2) * rib
solid_body = solid_body + rib_left + rib_right

hole = Cylinder(hole_diameter/2, hole_depth)
solid_body = solid_body - Pos(0, 0, knob_height - hole_depth/2) * hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "knob_with_ribs"
export_step(part, "output.step")