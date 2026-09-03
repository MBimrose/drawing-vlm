from build123d import *

base_length = 100.0
base_width = 50.0
base_thickness = 10.0
pocket_length = 80.0
pocket_width = 30.0
pocket_depth = 5.0
rib_height = 5.0
rib_width = 4.0
rib_spacing = 20.0
rib_edge_offset = 10.0
mount_hole_diameter = 3.0
mount_hole_offset_x = 15.0
mount_hole_offset_y = 10.0
chamfer_size = 0.5

result = Box(base_length, base_width, base_thickness)

pocket = Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

hole_positions = [
    (-base_length/2 + mount_hole_offset_x, -base_width/2 + mount_hole_offset_y),
    ( base_length/2 - mount_hole_offset_x, -base_width/2 + mount_hole_offset_y),
    (-base_length/2 + mount_hole_offset_x,  base_width/2 - mount_hole_offset_y),
    ( base_length/2 - mount_hole_offset_x,  base_width/2 - mount_hole_offset_y)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, base_thickness)

rib_count = int((base_length - 2 * rib_edge_offset) // rib_spacing) + 1
for i in range(rib_count):
    x = -base_length/2 + rib_edge_offset + i * rib_spacing
    rib = Pos(x, 0, -base_thickness/2 - rib_height/2) * Box(rib_width, rib_height, rib_height)
    result = result + rib

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "base_with_pocket_ribs"
export_step(part, "output.step")