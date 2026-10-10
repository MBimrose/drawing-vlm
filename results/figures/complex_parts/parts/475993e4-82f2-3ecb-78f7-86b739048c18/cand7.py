from build123d import *

base_length = 80.0
base_width = 40.0
base_thickness = 5.0
loft_height = 30.0
top_radius = 15.0
hole_diameter = 10.0
hole_depth = loft_height - 4.0
chamfer_size = 1.0
rib_width = 8.0
rib_height = 20.0
rib_offset = 12.0
slot_width = 5.0
slot_length = 30.0
slot_depth = base_thickness + 2.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Rectangle(base_length, base_width)
    with BuildSketch(Plane.XY.offset(loft_height)) as s2:
        Circle(top_radius)
    loft()

solid_body = p.part

rib1 = Pos(-base_length/2 + rib_offset, 0, rib_height/2) * Box(rib_width, base_thickness + rib_height, rib_height)
rib2 = Pos(base_length/2 - rib_offset, 0, rib_height/2) * Box(rib_width, base_thickness + rib_height, rib_height)
solid_body = solid_body + rib1 + rib2

hole = Pos(0, 0, loft_height - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
solid_body = solid_body - hole

slot = Pos(0, 0, loft_height/2 - slot_depth/2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "lofted_base_with_ribs"
export_step(part, "output.step")