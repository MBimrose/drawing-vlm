from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = 4.0
rib_spacing = 10.0
pocket_length = 60.0
pocket_width = 30.0
pocket_depth = 10.0
chamfer_size = 0.5
mount_hole_diameter = 3.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 20.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib_length = outer_length - 2 * wall_thickness
rib_count = int((outer_width - 2 * wall_thickness) // (rib_spacing + rib_thickness))
rib_positions = [-(outer_width/2 - wall_thickness - rib_thickness/2) + i*(rib_spacing + rib_thickness) for i in range(rib_count)]
for y in rib_positions:
    rib = Pos(0, y, outer_height - wall_thickness - rib_height/2) * Box(rib_length, rib_thickness, rib_height)
    solid_body = solid_body + rib

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

hole_positions = [
    (-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
    ( mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
    (-mount_hole_spacing_x/2,  mount_hole_spacing_y/2),
    ( mount_hole_spacing_x/2,  mount_hole_spacing_y/2),
]
for x, y in hole_positions:
    hole = Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)
    solid_body = solid_body - hole

part = solid_body
part.name = "shelled_box_with_ribs_pocket_holes"
export_step(part, "output.step")