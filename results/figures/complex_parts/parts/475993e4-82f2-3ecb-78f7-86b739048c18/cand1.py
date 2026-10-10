from build123d import *

base_width = 80.0
base_depth = 40.0
loft_height = 30.0
top_diameter = 30.0
hole_diameter = 10.0
hole_depth = loft_height - 4.0
chamfer_size = 1.0
rib_width = 8.0
rib_height = 15.0
rib_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Rectangle(base_width, base_depth)
    with BuildSketch(Plane.XY.offset(loft_height)) as s2:
        Circle(top_diameter / 2)
    loft()

solid_body = p.part

rib = Box(rib_width, rib_width, rib_height)
rib_left = Pos(-base_width/2 + rib_offset + rib_width/2, 0, rib_height/2) * rib
rib_right = Pos(base_width/2 - rib_offset - rib_width/2, 0, rib_height/2) * rib
solid_body = solid_body + rib_left + rib_right

hole = Pos(0, 0, loft_height - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "lofted_body_with_ribs"
export_step(part, "output.step")