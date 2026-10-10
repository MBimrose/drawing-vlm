from build123d import *
import math

outer_diameter = 60.0
body_length = 80.0
shaft_diameter = 20.0
shaft_length = 30.0
rib_height = 5.0
rib_width = 6.0
rib_count = 12
thread_diameter = 18.0
thread_length = 40.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
shaft_radius = shaft_diameter / 2.0
thread_radius = thread_diameter / 2.0

result = Pos(0, 0, body_length / 2) * Cylinder(outer_radius, body_length)
result = result + Pos(0, 0, -shaft_length / 2) * Cylinder(shaft_radius, shaft_length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius + rib_height / 2.0, 0, body_length / 2) * Box(rib_height, rib_width, body_length)
    result = result + rib

result = result - Pos(0, 0, -thread_length / 2) * Cylinder(thread_radius, thread_length)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

part = result
part.name = "ribbed_shaft_with_thread"
export_step(part, "output.step")