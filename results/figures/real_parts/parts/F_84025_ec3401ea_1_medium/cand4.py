from build123d import *
import math

base_width = 60.0
base_length = 80.0
base_thickness = 15.0
cyl_radius = 25.0
cyl_height = 45.0
central_hole_radius = 12.0
clearance_hole_radius = 3.0
clearance_hole_count = 6
clearance_hole_distance = 35.0
chamfer_size = 2.0
fillet_radius = 3.0

base = Box(base_width, base_length, base_thickness)
cyl = Pos(0, 0, base_thickness/2 + cyl_height/2) * Cylinder(cyl_radius, cyl_height)
solid_body = base + cyl

total_height = base_thickness + cyl_height
hole_z = cyl_height / 2
solid_body = solid_body - Pos(0, 0, hole_z) * Cylinder(central_hole_radius, total_height)

for i in range(clearance_hole_count):
    angle = math.radians(i * 360.0 / clearance_hole_count)
    px = clearance_hole_distance * math.cos(angle)
    py = clearance_hole_distance * math.sin(angle)
    solid_body = solid_body - Pos(px, py, hole_z) * Cylinder(clearance_hole_radius, total_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "base_with_cylinder_and_holes"
export_step(part, "output.step")