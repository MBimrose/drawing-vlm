from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 6.0
boss_radius = 8.0
boss_height = 6.0
hole_diameter = 3.2
hole_offset = 10.0
fillet_radius = 1.0

base = Pos(0, 0, plate_thickness / 2) * Box(plate_width, plate_depth, plate_thickness)
boss = Pos(0, 0, plate_thickness + boss_height / 2) * Cylinder(boss_radius, boss_height)
solid_body = base + boss

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

hole_r = hole_diameter / 2
hole_h = plate_thickness + boss_height + 10
for x, y in [(hole_offset, hole_offset), (plate_width - hole_offset, hole_offset),
             (hole_offset, plate_depth - hole_offset), (plate_width - hole_offset, plate_depth - hole_offset)]:
    solid_body = solid_body - Pos(x, y, plate_thickness + boss_height / 2) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")