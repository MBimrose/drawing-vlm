from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
housing_length = 60.0
shaft_bore_diameter = 30.0
counterbore_diameter = 45.0
counterbore_depth = 12.0
fillet_radius = 2.0
chamfer_distance = 1.5
rib_height = 8.0
rib_width = 6.0
rib_spacing_angle = 30.0
mount_hole_diameter = 6.0
mount_hole_rows = 2
mount_hole_cols = 3
mount_hole_spacing_x = 20.0
mount_hole_spacing_y = 15.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 5.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

result = Cylinder(outer_radius, housing_length)
result = result - Cylinder(shaft_bore_diameter / 2, housing_length + 2)
result = result - Pos(0, 0, housing_length / 2 - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)
result = result - Pos(0, 0, housing_length / 2 - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)

for i in range(mount_hole_cols):
    for j in range(mount_hole_rows):
        x = (i - (mount_hole_cols - 1) / 2) * mount_hole_spacing_x
        y = (j - (mount_hole_rows - 1) / 2) * mount_hole_spacing_y
        result = result - Pos(x, y, housing_length / 2 - (housing_length + 2) / 2) * Cylinder(mount_hole_diameter / 2, housing_length + 2)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

num_ribs = int(360 / rib_spacing_angle)
rib = Box(rib_width, rib_height, wall_thickness)
ribs = Pos(outer_radius - wall_thickness / 2, 0, 0) * rib
for i in range(1, num_ribs):
    ribs = ribs + Rot(0, 0, i * rib_spacing_angle) * Pos(outer_radius - wall_thickness / 2, 0, 0) * rib

result = result + ribs
top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "housing_with_ribs"
export_step(part, OUTPUT_PATH)