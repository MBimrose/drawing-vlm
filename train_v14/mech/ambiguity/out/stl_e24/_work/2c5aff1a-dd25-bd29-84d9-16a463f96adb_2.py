from build123d import *

outer_radius = 45.0
inner_radius = 30.0
housing_length = 70.0
rib_height = 10.0
rib_width = 20.0
rib_length = 30.0
rib_offset = 20.0
fillet_radius = 3.0
chamfer_distance = 2.0
mount_hole_diameter = 6.0
mount_hole_spacing = 35.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, housing_length))
            l3 = Line(l2@1, (inner_radius, housing_length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = fillet(bottom_face.edges(), fillet_radius)

rib = Pos(inner_radius - rib_height/2, 0, rib_offset + rib_length/2) * Box(rib_height, rib_width, rib_length)
solid_body = solid_body + rib

for x in [-mount_hole_spacing, mount_hole_spacing]:
    hole = Pos(x, 0, housing_length/4) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, housing_length)
    solid_body = solid_body - hole

part = solid_body
part.name = "housing_with_rib"
export_step(part, "output.step")