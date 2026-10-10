from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 15.0
boss_diameter = 50.0
boss_height = 45.0
hole_diameter = 8.0
hole_count = 6
hole_circle_radius = 35.0
chamfer_size = 2.0
fillet_radius = 3.0
shell_thickness = 0.65

base = Box(plate_width, plate_length, plate_thickness)
boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = base + boss

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

total_height = plate_thickness + boss_height
center_z = boss_height / 2
solid_body = solid_body - Pos(0, 0, center_z) * Cylinder(hole_diameter/2, total_height + 10)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, center_z) * Cylinder(hole_diameter/2, total_height + 10)

solid_body = offset(solid_body, amount=-shell_thickness)

part = solid_body
part.name = "plated_bossed_shelled"
export_step(part, "output.step")