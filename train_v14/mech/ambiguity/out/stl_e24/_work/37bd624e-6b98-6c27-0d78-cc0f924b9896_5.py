from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
rib_height = 4.0
rib_thickness = 2.0
rib_spacing = 10.0
chamfer_distance = 0.5
mount_hole_diameter = 3.0
mount_hole_offset_x = 15.0
mount_hole_offset_y = 10.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
shelled = offset(base, amount=-wall_thickness, openings=[top_face])

rib_positions = [-rib_spacing, 0, rib_spacing]
for y in rib_positions:
    rib = Pos(0, y, wall_thickness + inner_height/2 + rib_height/2) * Box(inner_length, rib_thickness, rib_height)
    shelled = shelled + rib

top_edges = shelled.faces().sort_by(Axis.Z)[-1].edges()
shelled = chamfer(top_edges, chamfer_distance)

hole_positions = [
    (-mount_hole_offset_x, -mount_hole_offset_y),
    (mount_hole_offset_x, -mount_hole_offset_y),
    (-mount_hole_offset_x, mount_hole_offset_y),
    (mount_hole_offset_x, mount_hole_offset_y),
]
for x, y in hole_positions:
    shelled = shelled - Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)

part = shelled
part.name = "shelled_box_with_ribs"
export_step(part, "output.step")