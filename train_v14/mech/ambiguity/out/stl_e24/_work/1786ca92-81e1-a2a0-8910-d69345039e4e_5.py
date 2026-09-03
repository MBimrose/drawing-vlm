from build123d import *

outer_radius = 20.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
length = 80.0
rib_height = 6.0
rib_width = 10.0
rib_thickness = 4.0
rib_position = length / 2.0
port_diameter = 8.0
port_center_z = length / 2.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib = Pos(outer_radius, 0, rib_position - rib_width / 2.0) * Box(rib_thickness, rib_height, rib_width)
solid_body = solid_body + rib

port = Pos(0, 0, port_center_z) * Rot(0, 90, 0) * Cylinder(port_diameter / 2.0, outer_radius * 2.0)
solid_body = solid_body - port

top_edges = solid_body.faces().sort_by(Axis.Z)[-1].edges()
solid_body = chamfer(top_edges, chamfer_size)
bottom_edges = solid_body.faces().sort_by(Axis.Z)[0].edges()
solid_body = chamfer(bottom_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_rib_and_port"
export_step(part, "output.step")