from build123d import *

cover_length = 80.0
cover_width = 50.0
cover_thickness = 5.0
wall_thickness = 3.0
pocket_depth = 2.0
chamfer_size = 0.5
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
rib_thickness = 2.0
rib_height = 2.0
rib_spacing = 20.0

base = Box(cover_length, cover_width, cover_thickness)

pocket = Box(cover_length - 2*wall_thickness, cover_width - 2*wall_thickness, pocket_depth)
base = base - pocket

hole_positions = [
    (-cover_length/2 + mount_hole_offset, -cover_width/2 + mount_hole_offset),
    ( cover_length/2 - mount_hole_offset, -cover_width/2 + mount_hole_offset),
    (-cover_length/2 + mount_hole_offset,  cover_width/2 - mount_hole_offset),
    ( cover_length/2 - mount_hole_offset,  cover_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    base = base - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, cover_thickness + 1)

rib_count = int((cover_length - 2*wall_thickness) // rib_spacing) + 1
for i in range(rib_count):
    x = -cover_length/2 + wall_thickness + i * rib_spacing
    rib = Pos(x, 0, -rib_height/2) * Box(rib_thickness, cover_width - 2*wall_thickness, rib_height)
    base = base + rib

bottom_face = base.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
base = chamfer(bottom_edges, chamfer_size)

part = base
part.name = "cover_plate"
export_step(part, "output.step")