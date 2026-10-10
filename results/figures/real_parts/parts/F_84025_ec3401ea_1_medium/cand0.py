from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 15.0
boss_diameter = 50.0
boss_height = 45.0
central_hole_diameter = 28.0
clearance_hole_diameter = 7.0
clearance_hole_count = 6
clearance_hole_radius = 35.0
chamfer_size = 2.0
fillet_radius = 3.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_length)
    extrude(amount=plate_thickness)
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s2:
        Circle(boss_diameter / 2)
    extrude(amount=boss_height)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

total_height = plate_thickness + boss_height
hole_depth = total_height + 10
z_center = total_height / 2

solid_body = solid_body - Pos(0, 0, z_center) * Cylinder(central_hole_diameter / 2, hole_depth)

for i in range(clearance_hole_count):
    angle = math.radians(i * 360.0 / clearance_hole_count)
    px = clearance_hole_radius * math.cos(angle)
    py = clearance_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, z_center) * Cylinder(clearance_hole_diameter / 2, hole_depth)

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")