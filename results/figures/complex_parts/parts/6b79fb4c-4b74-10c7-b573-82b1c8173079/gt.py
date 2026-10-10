from build123d import *
import math

overall_width = 80
overall_height = 40
wall_thickness = 5
length = 100
slot_width = 15
blind_hole_diameter = 8
blind_hole_depth = 20
pattern_hole_diameter = 3
pattern_rows = 3
pattern_cols = 4
pattern_spacing = 12
chamfer_dist = 2
rib_width = 30
rib_height = 20
rib_depth = 3

result = Box(overall_width, length, overall_height)

inner_width = overall_width - wall_thickness
inner_height = overall_height - wall_thickness
pocket_center_x = -overall_width/2 + wall_thickness + inner_width/2
result = result - Pos(pocket_center_x, 0, 0) * Box(inner_width, length, inner_height)

result = result - Pos(0, 0, overall_height/2 - wall_thickness/2) * Box(slot_width, length, wall_thickness)

result = result - Pos(-overall_width/2 + rib_depth/2, 0, 0) * Box(rib_depth, rib_width, rib_height)

result = result - Pos(-overall_width/2 + blind_hole_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

for i in range(pattern_rows):
    for j in range(pattern_cols):
        y_off = (j - (pattern_cols-1)/2) * pattern_spacing
        z_off = (i - (pattern_rows-1)/2) * pattern_spacing
        result = result - Pos(-overall_width/2 + blind_hole_depth/2, y_off, z_off) * Rot(0, 90, 0) * Cylinder(pattern_hole_diameter/2, blind_hole_depth)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_dist)

part = result
part.name = "c_channel_with_features"
export_step(part, OUTPUT_PATH)