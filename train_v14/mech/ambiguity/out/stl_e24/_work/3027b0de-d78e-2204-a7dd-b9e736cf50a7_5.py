from build123d import *

length = 100.0
width = 50.0
thickness = 10.0
pocket_margin = 10.0
pocket_depth = 4.0
rib_width = 5.0
rib_height = 5.0
rib_spacing = 20.0
mount_hole_diameter = 3.0
mount_hole_offset_x = 15.0
mount_hole_offset_y = 10.0
chamfer_size = 0.5

solid_body = Box(length, width, thickness)

pocket_w = length - 2 * pocket_margin
pocket_h = width - 2 * pocket_margin
pocket = Pos(0, 0, -thickness/2 + pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)
solid_body = solid_body - pocket

num_ribs = int((length - 2 * pocket_margin) // rib_spacing) + 1
rib_positions = [-length/2 + pocket_margin + i * rib_spacing for i in range(num_ribs)]
for x in rib_positions:
    rib = Pos(x, 0, -thickness/2 - rib_height/2) * Box(rib_width, rib_height, rib_height)
    solid_body = solid_body + rib

hole_r = mount_hole_diameter / 2
hole_h = thickness + 2
hole_pts = [
    (-length/2 + mount_hole_offset_x, -width/2 + mount_hole_offset_y),
    ( length/2 - mount_hole_offset_x, -width/2 + mount_hole_offset_y),
    (-length/2 + mount_hole_offset_x,  width/2 - mount_hole_offset_y),
    ( length/2 - mount_hole_offset_x,  width/2 - mount_hole_offset_y),
]
for x, y in hole_pts:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "ribbed_plate_with_pocket"
export_step(part, "output.step")