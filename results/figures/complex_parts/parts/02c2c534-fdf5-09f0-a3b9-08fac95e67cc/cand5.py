from build123d import *

base_diameter = 20.0
tip_diameter = 5.0
length = 70.0
rib_height = 10.0
rib_width = 30.0
rib_thickness = 4.0
mid_rib_height = 8.0
mid_rib_width = 20.0
mid_rib_thickness = 3.0
tip_rib_height = 5.0
tip_rib_width = 10.0
tip_rib_thickness = 2.0
hole_diameter = 4.0
slot_width = 6.0
slot_depth = 3.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_diameter / 2)
    with BuildSketch(Plane.XY.offset(length)) as s2:
        Circle(tip_diameter / 2)
    loft()

solid_body = p.part

rib1 = Pos(0, 0, rib_height / 2) * Box(rib_width, rib_thickness, rib_height)
rib2 = Pos(0, 0, length / 2 + mid_rib_height / 2) * Box(mid_rib_width, mid_rib_thickness, mid_rib_height)
rib3 = Pos(0, 0, length - tip_rib_height / 2) * Box(tip_rib_width, tip_rib_thickness, tip_rib_height)

solid_body = solid_body + rib1 + rib2 + rib3

solid_body = solid_body - Pos(0, 0, length / 2) * Cylinder(hole_diameter / 2, length + 20)

slot = Pos(0, 0, length / 2 - slot_depth / 2) * Box(slot_width, length, slot_depth)
solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "lofted_ribbed_part"
export_step(part, "output.step")