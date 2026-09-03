from build123d import *

outer_diameter = 50.0
inner_diameter = 21.0
thickness = 10.0
keyway_width = 6.0
keyway_depth = 4.0
chamfer_distance = 0.5
mount_hole_diameter = 4.5
mount_hole_spacing = 30.0
rib_height = 3.0
rib_width = 8.0
rib_offset = 10.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=thickness)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, thickness/2) * Cylinder(inner_radius, thickness)

solid_body = solid_body - Pos(inner_radius + keyway_depth/2.0, 0, thickness/2) * Box(keyway_depth, keyway_width, thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

for x in [-mount_hole_spacing/2.0, mount_hole_spacing/2.0]:
    solid_body = solid_body - Pos(x, 0, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)

solid_body = solid_body + Pos(rib_offset, 0, thickness/2) * Box(rib_width, rib_height, thickness)

part = solid_body
part.name = "collar_with_keyway"
export_step(part, "output.step")