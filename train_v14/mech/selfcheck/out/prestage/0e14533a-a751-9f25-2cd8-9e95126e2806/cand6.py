from build123d import *

block_width = 80.0
block_depth = 50.0
block_height = 60.0
wall_thickness = 4.0
bore_diameter = 16.0
bore_depth = 45.0
counterbore_diameter = 24.0
counterbore_depth = 10.0
fillet_radius = 3.0
chamfer_distance = 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
rib_width = 10.0
rib_height = 5.0
rib_offset = 12.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_width, block_depth)
    extrude(amount=block_height)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, block_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - Pos(0, 0, block_height - bore_depth/2) * Cylinder(bore_diameter/2, bore_depth)

solid_body = solid_body + Pos(0, rib_offset, block_height + rib_height/2) * Box(rib_width, rib_height, rib_height)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, block_depth/2, block_height) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_depth + 10)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

top_y_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = fillet(top_y_face.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "block_with_bore_and_rib"
export_step(part, "output.step")