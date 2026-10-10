from build123d import *

inner_dia = 19.6
outer_dia = 38.0
collar_length = 15.0
inner_radius = inner_dia / 2
outer_radius = outer_dia / 2
set_screw_dia = 3.0
set_screw_depth = 5.0
set_screw_head_dia = 6.0
set_screw_head_height = 2.5
chamfer_size = 0.4
rib_height = 2.0
rib_thickness = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, collar_length))
            l2 = Line(l1 @ 1, (outer_radius, collar_length))
            l3 = Line(l2 @ 1, (outer_radius, 0))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_edges = solid_body.edges().sort_by(Axis.Z)[-2:]
solid_body = chamfer(top_edges, chamfer_size)

rib = Pos(0, 0, collar_length + rib_height / 2) * Box(rib_thickness, outer_dia, rib_height)
solid_body = solid_body + rib

with BuildPart() as hp:
    with BuildSketch() as hs:
        RegularPolygon(set_screw_head_dia / 2, 6)
    extrude(amount=set_screw_head_height)
hex_prism = hp.part
solid_body = solid_body - Pos(0, 0, collar_length + rib_height - set_screw_head_height) * hex_prism

hole = Cylinder(set_screw_dia / 2, set_screw_depth)
solid_body = solid_body - Pos(0, 0, collar_length + rib_height - set_screw_depth / 2) * hole

part = solid_body
part.name = "set_screw_collar"
export_step(part, OUTPUT_PATH)