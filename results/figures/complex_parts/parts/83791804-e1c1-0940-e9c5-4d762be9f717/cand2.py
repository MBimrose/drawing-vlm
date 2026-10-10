from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 6.0
central_hole_diameter = 30.0
mount_hole_diameter = 6.0
mount_hole_offset = 12.0
rib_width = 4.0
rib_height = 30.0
rib_depth = 4.0
chamfer_size = 0.5
vent_hole_diameter = 5.0
vent_spacing_x = 20.0
vent_spacing_y = 12.0
vent_rows = 2
vent_cols = 3

result = Box(plate_width, plate_thickness, plate_height)
result = result - Rot(90, 0, 0) * Cylinder(central_hole_diameter / 2, plate_thickness)

mount_points = [
    (-plate_width / 2 + mount_hole_offset, 0),
    (plate_width / 2 - mount_hole_offset, 0)
]
for x, z in mount_points:
    result = result - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter / 2, plate_thickness)

vent_points = []
for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols - 1) / 2) * vent_spacing_x
        z = (j - (vent_rows - 1) / 2) * vent_spacing_y
        vent_points.append((x, z))
for x, z in vent_points:
    result = result - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(vent_hole_diameter / 2, plate_thickness)

result = result + Pos(plate_width / 2 + rib_depth / 2, -plate_height / 2 + rib_height / 2, 0) * Box(rib_depth, rib_width, rib_height)
result = result + Pos(-plate_width / 2 - rib_depth / 2, -plate_height / 2 + rib_height / 2, 0) * Box(rib_depth, rib_width, rib_height)

top_face = result.faces().sort_by(Axis.Y)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "plate_with_holes_and_ribs"
export_step(part, "output.step")