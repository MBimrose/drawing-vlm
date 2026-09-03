from build123d import *

outer_diameter = 80.0
inner_diameter = 40.0
length = 80.0
keyway_width = 12.0
keyway_depth = 6.0
set_screw_diameter = 8.0
set_screw_offset = 30.0
chamfer_distance = 1.5
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
rib_width = 10.0
rib_height = 20.0
rib_thickness = 5.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, length))
            l2 = Line(l1@1, (inner_radius, length))
            l3 = Line(l2@1, (inner_radius, 0))
            l4 = Line(l3@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

solid_body = solid_body - Pos(set_screw_offset, 0, length/2) * Cylinder(set_screw_diameter/2, length + 10)

for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2),
             (mount_hole_spacing/2, -mount_hole_spacing/2),
             (mount_hole_spacing/2, mount_hole_spacing/2),
             (-mount_hole_spacing/2, mount_hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, length/2) * Cylinder(mount_hole_diameter/2, length + 10)

solid_body = solid_body - Pos(inner_radius - keyway_depth/2, 0, length/2) * Box(keyway_width, keyway_depth, length)

solid_body = solid_body + Pos(0, 0, length + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)

part = solid_body
part.name = "hollow_cylinder_with_keyway"
export_step(part, "output.step")