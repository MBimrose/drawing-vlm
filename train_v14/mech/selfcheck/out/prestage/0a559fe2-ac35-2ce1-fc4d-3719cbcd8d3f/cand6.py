from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = outer_height - 2 * wall_thickness
rib_spacing = 20.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 10.0
chamfer_size = 1.0
mount_hole_diameter = 3.0
mount_hole_spacing = 20.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

rib_count = int((outer_length - 2 * wall_thickness) // rib_spacing)
for i in range(rib_count):
    x_pos = -outer_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, wall_thickness + rib_height/2) * Box(rib_thickness, outer_width - 2*wall_thickness, rib_height)
    solid_body = solid_body + rib

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

front_face = solid_body.faces().sort_by(Axis.Y)[-1]
front_edges = front_face.edges()
solid_body = chamfer(front_edges, chamfer_size)

hole_r = mount_hole_diameter / 2
for y_off in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(outer_length/2, y_off, outer_height/2 + outer_height/2 - wall_thickness - 5) * Rot(0, 90, 0) * Cylinder(hole_r, outer_length)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_box_with_ribs_pocket"
export_step(part, "output.step")