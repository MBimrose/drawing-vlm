from build123d import *

body_length = 80
body_outer_dia = 40
wall_thickness = 3
inner_dia = body_outer_dia - 2 * wall_thickness
groove_width = 10
groove_depth = 2
groove_length = 30
groove_start = 20
port_dia = 8
port_offset = 15
rib_width = 6
rib_height = 10
rib_thickness = 2
rib_offset = 30

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(body_outer_dia / 2)
    extrude(amount=body_length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

groove_box = Pos(0, 0, groove_start + groove_length / 2) * Box(groove_width, groove_depth, groove_length)
solid_body = solid_body - groove_box

port_cyl = Pos(body_outer_dia / 2, 0, body_length / 2) * Rot(0, 90, 0) * Cylinder(port_dia / 2, body_outer_dia + 10)
solid_body = solid_body - port_cyl

rib_box = Pos(body_outer_dia / 2 + rib_thickness / 2, 0, rib_offset + rib_height / 2) * Box(rib_thickness, rib_width, rib_height)
solid_body = solid_body + rib_box

part = solid_body
part.name = "hollow_cylinder_with_groove_port_rib"
export_step(part, "output.step")