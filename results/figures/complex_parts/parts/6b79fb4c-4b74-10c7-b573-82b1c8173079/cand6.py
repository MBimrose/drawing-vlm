from build123d import *

outer_width = 80.0
outer_height = 100.0
depth = 40.0
wall_thickness = 5.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 10.0
chamfer_size = 2.0
hole_diameter = 8.0
vent_hole_diameter = 3.0
vent_rows = 4
vent_cols = 3
vent_spacing_x = 12.0
vent_spacing_y = 12.0
slot_width = 20.0
slot_length = 30.0

base = Box(outer_width, outer_height, depth)
inner_cut = Pos(wall_thickness/2, 0, 0) * Box(outer_width - wall_thickness, outer_height - 2*wall_thickness, depth)
result = base - inner_cut

pocket = Pos(-outer_width/2 + pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
result = result - pocket

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

result = result - Pos(-outer_width/2 + depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, depth)

for i in range(vent_cols):
    for j in range(vent_rows):
        y = (i - (vent_cols-1)/2) * vent_spacing_x
        z = (j - (vent_rows-1)/2) * vent_spacing_y
        result = result - Pos(-outer_width/2 + depth/2, y, z) * Rot(0, 90, 0) * Cylinder(vent_hole_diameter/2, depth)

slot = Pos(0, 0, depth/2 - wall_thickness/2) * Box(slot_width, slot_length, wall_thickness)
result = result - slot

part = result
part.name = "channel_with_pocket_and_vents"
export_step(part, "output.step")