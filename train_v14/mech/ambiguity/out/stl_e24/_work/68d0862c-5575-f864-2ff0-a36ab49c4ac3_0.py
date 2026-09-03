from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
corner_radius = 5.0
wall_thickness = 2.0
boss_diameter = 20.0
boss_height = 6.0
hole_diameter = 6.0
hole_offset_x = 20.0
hole_offset_y = 15.0

base = Box(plate_length, plate_width, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), corner_radius)

boss = Cylinder(boss_diameter / 2, boss_height)
solid_body = base + boss

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

for x, y in [(-hole_offset_x, -hole_offset_y), (hole_offset_x, hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness + boss_height + 10)

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")