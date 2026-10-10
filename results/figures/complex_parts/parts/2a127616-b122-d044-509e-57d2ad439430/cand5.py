from build123d import *

outer_radius = 30.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
length = 80.0
knurl_height = 2.0
knurl_width = 6.0
knurl_count = 12
shaft_radius = 10.0
shaft_length = 30.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, length))
            l3 = Line(l2@1, (inner_radius, length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body + Pos(0, 0, -shaft_length/2) * Cylinder(shaft_radius, shaft_length)

for i in range(knurl_count):
    angle = i * 360.0 / knurl_count
    rib = Rot(0, 0, angle) * Pos(outer_radius + knurl_height/2, 0, length/2) * Box(knurl_width, knurl_height, length)
    solid_body = solid_body + rib

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "knurled_shaft_collar"
export_step(part, "output.step")