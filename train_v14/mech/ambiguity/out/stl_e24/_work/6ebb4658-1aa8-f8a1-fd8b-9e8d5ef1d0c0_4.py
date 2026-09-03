from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 4.0
central_hole_diameter = 12.0
counterbore_diameter = 20.0
counterbore_depth = 10.0
rib_thickness = 5.0
rib_height = 5.0
rib_spacing = 15.0
mount_hole_diameter = 5.0
mount_hole_offset = 5.0
chamfer_distance = 1.0

result = Box(block_length, block_width, block_height)

result = result - Cylinder(central_hole_diameter/2, block_height)
result = result - Pos(0, 0, block_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

mount_hole = Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width)
for x in [-block_length/2 + wall_thickness/2, block_length/2 - wall_thickness/2]:
    for z in [block_height/2 - mount_hole_offset, -block_height/2 + mount_hole_offset]:
        result = result - Pos(x, 0, z) * mount_hole

rib = Box(rib_thickness, block_width - 2*wall_thickness, rib_height)
num_ribs = int((block_length - 2*wall_thickness) // rib_spacing) + 1
for i in range(num_ribs):
    x = -block_length/2 + wall_thickness + i * rib_spacing
    result = result + Pos(x, 0, -block_height/2 + rib_height/2) * rib

top_face = result.faces().sort_by(Axis.Z)[-1]
bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(top_face.edges() + bottom_face.edges(), chamfer_distance)

part = result
part.name = "block_with_ribs_and_holes"
export_step(part, "output.step")