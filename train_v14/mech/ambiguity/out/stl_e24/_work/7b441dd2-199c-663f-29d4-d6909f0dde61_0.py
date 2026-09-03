from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 10.0
central_hole_diameter = 25.4
mount_hole_diameter = 6.3
mount_hole_offset_x = 20.0
mount_hole_offset_y = 10.0
boss_diameter = 20.0
boss_height = 5.0
chamfer_distance = 1.0
counterbore_diameter = 12.7
counterbore_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Cylinder(central_hole_diameter/2, plate_thickness)

mount_points = [
    (-mount_hole_offset_x, -mount_hole_offset_y),
    (mount_hole_offset_x, -mount_hole_offset_y),
    (-mount_hole_offset_x, mount_hole_offset_y),
    (mount_hole_offset_x, mount_hole_offset_y),
]

for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness)
    solid_body = solid_body - Pos(x, y, plate_thickness - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

solid_body = solid_body + Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = chamfer(solid_body.edges(), chamfer_distance)

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")