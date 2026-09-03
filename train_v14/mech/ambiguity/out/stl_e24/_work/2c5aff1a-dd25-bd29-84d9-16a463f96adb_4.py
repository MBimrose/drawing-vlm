from build123d import *

outer_radius = 45.0
inner_radius = 30.0
housing_length = 70.0
wall_thickness = outer_radius - inner_radius
keyway_width = 20.0
keyway_depth = 8.0
keyway_length = 30.0
fillet_radius = 4.0
mount_hole_diameter = 6.0
mount_hole_spacing = 40.0
rib_thickness = 3.0
rib_height = 10.0
rib_length = housing_length * 0.8

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
solid_body = fillet(solid_body.edges(), fillet_radius)

keyway_box = Pos(inner_radius - keyway_depth/2, 0, housing_length/2) * Box(keyway_depth, keyway_width, keyway_length)
solid_body = solid_body - keyway_box

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, housing_length * 0.25) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, housing_length)
    solid_body = solid_body - hole

rib = Pos(inner_radius - rib_thickness/2, 0, housing_length/2) * Box(rib_thickness, rib_height, rib_length)
solid_body = solid_body + rib

part = solid_body
part.name = "housing_with_keyway"
export_step(part, "output.step")