from build123d import *

outer_diameter = 30.0
inner_diameter = 12.0
height = 15.0
chamfer_size = 1.0
rib_width = 4.0
rib_height = 2.0
rib_thickness = 2.0
rib_offset_from_top = 3.0
hole_diameter = 5.0
hole_offset = 6.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, height))
            l3 = Line(l2 @ 1, (inner_radius, height))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

rib = Pos(outer_radius, 0, height - rib_offset_from_top - rib_height / 2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

for y_off in [hole_offset, -hole_offset]:
    hole = Pos(outer_radius, y_off, height / 2) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, outer_diameter + 1)
    solid_body = solid_body - hole

part = solid_body
part.name = "revolved_ring_with_rib_and_holes"
export_step(part, "output.step")