from build123d import *

base_length = 100.0
base_width = 50.0
base_thickness = 10.0
pocket_length = 80.0
pocket_width = 30.0
pocket_depth = 4.0
rib_width = 5.0
rib_height = 5.0
rib_spacing = 20.0
chamfer_size = 0.5
mount_hole_dia = 3.0
mount_hole_offset_x = 35.0
mount_hole_offset_y = 15.0

solid = Box(base_length, base_width, base_thickness)

pocket = Pos(0, 0, -pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid = solid - pocket

num_ribs = int(base_length / rib_spacing) + 1
for i in range(num_ribs):
    x = (i - (num_ribs - 1) / 2) * rib_spacing
    rib = Pos(x, 0, -base_thickness/2 - rib_height/2) * Box(rib_width, rib_height, rib_height)
    solid = solid + rib

top_face = solid.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid = chamfer(top_edges, chamfer_size)

hole_positions = [
    (mount_hole_offset_x, mount_hole_offset_y),
    (-mount_hole_offset_x, mount_hole_offset_y),
    (mount_hole_offset_x, -mount_hole_offset_y),
    (-mount_hole_offset_x, -mount_hole_offset_y)
]
for x, y in hole_positions:
    hole = Pos(x, y, 0) * Cylinder(mount_hole_dia/2, base_thickness + 2)
    solid = solid - hole

part = solid
part.name = "base_plate_with_pocket_ribs"
export_step(part, "output.step")