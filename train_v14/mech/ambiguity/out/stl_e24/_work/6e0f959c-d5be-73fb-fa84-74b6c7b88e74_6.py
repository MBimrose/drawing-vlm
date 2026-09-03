from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 15.0
wall_thickness = 2.0
vent_slot_width = 30.0
vent_slot_height = 10.0
vent_slot_depth = 4.0
mount_hole_diameter = 2.5
mount_hole_spacing_x = 25.0
mount_hole_spacing_y = 25.0
mount_hole_rows = 2
mount_hole_cols = 2
chamfer_distance = 1.0
rib_thickness = 1.5
rib_height = 5.0
rib_spacing = 12.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[bottom_face])

vent_cut = Pos(-outer_length/2 + vent_slot_depth/2, 0, outer_height/2) * Box(vent_slot_depth, vent_slot_width, vent_slot_height)
base = base - vent_cut

for i in range(mount_hole_cols):
    for j in range(mount_hole_rows):
        x = (i - (mount_hole_cols-1)/2) * mount_hole_spacing_x
        y = (j - (mount_hole_rows-1)/2) * mount_hole_spacing_y
        base = base - Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)

front_face = base.faces().sort_by(Axis.Y)[-1]
front_edges = front_face.edges().filter_by(Axis.Z)
base = chamfer(front_edges, chamfer_distance)

rib = Pos(outer_length/2 - wall_thickness - rib_thickness/2, -outer_width/2 + wall_thickness + rib_spacing/2, outer_height/2) * Box(rib_thickness, rib_spacing, rib_height)
base = base + rib

part = base
part.name = "ventilated_enclosure"
export_step(part, "output.step")