from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_spacing = 20.0
front_chamfer = 1.0
mount_hole_diameter = 3.0
mount_hole_spacing = 20.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])
front_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = chamfer(front_face.edges(), front_chamfer)
rib_count = int((outer_length - 2 * wall_thickness) // rib_spacing)
for i in range(rib_count):
    x_pos = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x_pos, 0, outer_height/2) * Box(rib_thickness, outer_width - 2 * wall_thickness, outer_height - 2 * wall_thickness)
    solid_body = solid_body + rib
hole_r = mount_hole_diameter / 2
hole_h = outer_length + 10
for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(outer_length/2, y, outer_height - wall_thickness - 5) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
part = solid_body
part.name = "shelled_box_with_ribs"
export_step(part, "output.step")