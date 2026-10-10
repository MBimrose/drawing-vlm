from build123d import *

body_diameter = 80.0
body_length = 100.0
wall_thickness = 5.0
bore_diameter = 30.0
shoulder_diameter = 60.0
shoulder_length = 20.0
rib_height = 5.0
rib_width = 20.0
rib_position = 40.0
port_diameter = 30.0
port_offset = 40.0
chamfer_size = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((bore_diameter/2, 0), (body_diameter/2, 0))
            l2 = Line(l1@1, (body_diameter/2, rib_position))
            l3 = Line(l2@1, ((body_diameter/2)+rib_height, rib_position))
            l4 = Line(l3@1, ((body_diameter/2)+rib_height, rib_position+rib_width))
            l5 = Line(l4@1, (body_diameter/2, rib_position+rib_width))
            l6 = Line(l5@1, (body_diameter/2, body_length-shoulder_length))
            l7 = Line(l6@1, (shoulder_diameter/2, body_length-shoulder_length))
            l8 = Line(l7@1, (shoulder_diameter/2, body_length))
            l9 = Line(l8@1, (bore_diameter/2, body_length))
            l10 = Line(l9@1, (bore_diameter/2, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(port_offset, body_length/2, body_length/2) * Rot(90, 0, 0) * Cylinder(port_diameter/2, body_length)
solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "revolved_body_with_port"
export_step(part, "output.step")