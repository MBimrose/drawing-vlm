from build123d import *

base_length = 80.0
base_width = 40.0
base_height = 30.0
top_diameter = 30.0
rib_width = 10.0
rib_thickness = 8.0
rib_height = 20.0
rib_offset = 30.0
hole_diameter = 10.0
hole_depth = base_height - 4.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Rectangle(base_length, base_width)
    with BuildSketch(Plane.XY.offset(base_height)) as s2:
        Circle(top_diameter / 2)
    loft()

solid_body = p.part

rib = Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + Pos(-rib_offset, 0, rib_height / 2) * rib
solid_body = solid_body + Pos(rib_offset, 0, rib_height / 2) * rib

hole = Cylinder(hole_diameter / 2, hole_depth)
solid_body = solid_body - Pos(0, 0, base_height - hole_depth / 2) * hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "lofted_base_with_ribs"
export_step(part, "output.step")