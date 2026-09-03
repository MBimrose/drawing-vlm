from build123d import *

outer_diameter = 60.0
inner_diameter = 30.0
length = 60.0
counterbore_diameter = 50.0
counterbore_depth = 15.0
fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0
mount_hole_offset = 10.0
groove_width = 5.0
groove_depth = 3.0
groove_position = 30.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
counterbore_radius = counterbore_diameter / 2.0
wall_thickness = outer_radius - inner_radius

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, length - counterbore_depth))
            l2 = Line(l1@1, (counterbore_radius, length - counterbore_depth))
            l3 = Line(l2@1, (counterbore_radius, length))
            l4 = Line(l3@1, (outer_radius, length))
            l5 = Line(l4@1, (outer_radius, 0))
            l6 = Line(l5@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, length * 2)

groove = Pos(0, 0, groove_position) * Cylinder(inner_radius - groove_depth, groove_width)
solid_body = solid_body - groove

part = solid_body
part.name = "revolved_shaft_with_groove"
export_step(part, "output.step")