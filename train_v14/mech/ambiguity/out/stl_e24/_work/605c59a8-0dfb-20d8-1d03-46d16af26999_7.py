from build123d import *

base_length = 100.0
base_width = 60.0
base_thickness = 8.0
rib_height = 30.0
rib_width = 20.0
rib_length = 80.0
rib_draft_angle = 5.0
mount_hole_dia = 5.0
mount_hole_offset = 10.0
pocket_depth = 4.0
pocket_width = 12.0
pocket_length = 60.0
chamfer_size = 0.5

with BuildPart() as p:
    Box(base_length, base_width, base_thickness)
    with BuildSketch(Plane.XY.offset(base_thickness/2)) as s:
        Rectangle(rib_length, rib_width)
    extrude(amount=rib_height, taper=rib_draft_angle)

solid_body = p.part

hole_positions = [
    (-base_length/2 + mount_hole_offset, -base_width/2 + mount_hole_offset),
    ( base_length/2 - mount_hole_offset, -base_width/2 + mount_hole_offset),
    ( base_length/2 - mount_hole_offset,  base_width/2 - mount_hole_offset),
    (-base_length/2 + mount_hole_offset,  base_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, base_thickness + 1)

solid_body = solid_body - Pos(0, 0, base_thickness/2 + rib_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "base_plate_with_rib"
export_step(part, "output.step")