from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 4.0
step_diameter = 12.0
step_depth = 20.0
counterbore_diameter = 20.0
counterbore_depth = 10.0
fillet_radius = 2.0
chamfer_distance = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
rib_thickness = 3.0
rib_height = 15.0
rib_spacing = 20.0

solid = Box(block_length, block_width, block_height)

bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = chamfer(bottom_face.edges(), chamfer_distance)

solid = solid - Pos(0, 0, block_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid = solid - Pos(0, 0, block_height/2 - step_depth/2) * Cylinder(step_diameter/2, step_depth)

solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)

hole_y = block_width / 2
hole_z = block_height / 2 - mount_hole_offset
hole_x_positions = [-(block_length / 2 - wall_thickness / 2), (block_length / 2 - wall_thickness / 2)]
for x in hole_x_positions:
    solid = solid - Pos(x, 0, hole_z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width + 10)

rib_count = int((block_length - 2 * wall_thickness) // rib_spacing) + 1
rib_x_positions = [-(block_length / 2 - wall_thickness) + i * rib_spacing for i in range(rib_count)]
for x in rib_x_positions:
    solid = solid + Pos(x, 0, -block_height/2 + rib_height/2) * Box(rib_thickness, block_width - 2 * wall_thickness, rib_height)

part = solid
part.name = "stepped_bore_block_with_ribs"
export_step(part, "output.step")