from build123d import *
import math

plate_width = 60.0
plate_length = 80.0
plate_thickness = 15.0
boss_diameter = 50.0
boss_height = 45.0
hole_diameter = 8.0
hole_pattern_radius = 35.0
fillet_radius = 2.0
chamfer_distance = 1.0
rib_width = 10.0
rib_height = 20.0
rib_thickness = 5.0

base = Box(plate_width, plate_length, plate_thickness)
boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
rib = Pos(boss_diameter/2 - rib_thickness/2, 0, plate_thickness/2 + rib_height/2) * Box(rib_thickness, rib_width, rib_height)

solid_body = base + boss + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

hole_h = plate_thickness + boss_height + 20
solid_body = solid_body - Cylinder(hole_diameter/2, hole_h)

for i in range(6):
    angle = math.radians(i * 60)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter/2, hole_h)

part = solid_body
part.name = "plate_with_boss_and_ribs"
export_step(part, "output.step")