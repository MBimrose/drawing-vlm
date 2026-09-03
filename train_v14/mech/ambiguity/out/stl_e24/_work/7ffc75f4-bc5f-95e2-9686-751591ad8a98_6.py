from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_width = 30.0
vent_height = 10.0
fillet_radius = 1.0
mount_hole_dia = 3.0
mount_hole_offset = 5.0
rib_thickness = 2.0
rib_height = 5.0
rib_spacing = 20.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

vent_cut = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(vent_width, wall_thickness, vent_height)
base = base - vent_cut

hole_positions = [
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
    (-outer_length/2 + mount_hole_offset,  outer_width/2 - mount_hole_offset),
    ( outer_length/2 - mount_hole_offset,  outer_width/2 - mount_hole_offset)
]
for x, y in hole_positions:
    base = base - Pos(x, y, outer_height/2) * Cylinder(mount_hole_dia/2, outer_height)

rib_count = int((outer_length - 2*wall_thickness) // rib_spacing)
for i in range(rib_count):
    x_pos = -outer_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, wall_thickness + rib_height/2) * Box(rib_thickness, outer_width - 2*wall_thickness, rib_height)
    base = base + rib

part = base
part.name = "ventilated_enclosure"
export_step(part, "output.step")