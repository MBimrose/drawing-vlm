from build123d import *
import math

block_width = 80.0
block_depth = 50.0
block_height = 60.0
rib_width = 20.0
rib_depth = 10.0
rib_height = 5.0
rib_offset_y = 15.0
central_hole_radius = 8.0
countersink_radius = 12.0
countersink_angle = 90.0
mount_hole_radius = 3.0
mount_hole_spacing = 30.0
chamfer_distance = 2.0
fillet_radius = 3.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_width, block_depth)
    extrude(amount=block_height)

solid_body = p.part

rib = Pos(0, rib_offset_y, rib_height/2) * Box(rib_width, rib_depth, rib_height)
solid_body = solid_body + rib

csk_depth = (countersink_radius - central_hole_radius) / math.tan(math.radians(countersink_angle / 2))
shaft_depth = block_height - csk_depth

csk_cone = Pos(0, 0, block_height - csk_depth/2) * Cone(central_hole_radius, countersink_radius, csk_depth)
shaft_cyl = Pos(0, 0, block_height - csk_depth - shaft_depth/2) * Cylinder(central_hole_radius, shaft_depth)
solid_body = solid_body - csk_cone - shaft_cyl

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, block_height) * Rot(90, 0, 0) * Cylinder(mount_hole_radius, block_depth + 10)
    solid_body = solid_body - hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

top_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = fillet(top_face.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "block_with_rib_and_holes"
export_step(part, "output.step")