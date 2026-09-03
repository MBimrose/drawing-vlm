from build123d import *

base_length = 100.0
base_width = 50.0
base_thickness = 10.0
pocket_length = 80.0
pocket_width = 30.0
pocket_depth = 6.0
rib_height = 5.0
rib_thickness = 4.0
rib_spacing = 15.0
mount_hole_diameter = 3.0
mount_hole_offset_x = 35.0
mount_hole_offset_y = 15.0
chamfer_size = 0.5

result = Box(base_length, base_width, base_thickness)

pocket = Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

rib_count = int(base_length // rib_spacing)
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, -base_thickness/2 - rib_height/2) * Box(rib_thickness, rib_height, rib_height)
    result = result + rib

hole_positions = [
    (mount_hole_offset_x, mount_hole_offset_y),
    (-mount_hole_offset_x, mount_hole_offset_y),
    (mount_hole_offset_x, -mount_hole_offset_y),
    (-mount_hole_offset_x, -mount_hole_offset_y),
]
for x, y in hole_positions:
    hole = Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, base_thickness + 1)
    result = result - hole

top_face = result.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "base_plate_with_pocket_ribs"
export_step(part, "output.step")