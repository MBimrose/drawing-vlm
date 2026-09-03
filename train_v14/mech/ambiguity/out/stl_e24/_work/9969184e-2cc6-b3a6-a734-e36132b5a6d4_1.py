from build123d import *
import math

coupler_length = 80.0
outer_diameter = 40.0
inner_diameter = 20.0
thread_pitch = 4.0
thread_depth = 2.0
thread_angle = 30.0
keyway_width = 6.0
keyway_depth = 4.0
chamfer_size = 0.5
mount_hole_diameter = 6.0
mount_hole_offset = 12.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
thread_turns = coupler_length / (thread_pitch * 2.0)
thread_angle_rad = math.radians(thread_angle)
thread_width = 2.0 * thread_depth * math.tan(thread_angle_rad)

result = Cylinder(outer_radius, coupler_length)
result = result - Cylinder(inner_radius, coupler_length)

with BuildPart() as thread_bp:
    with BuildSketch() as thread_sk:
        Rectangle(thread_width, thread_depth)
    extrude(amount=coupler_length, taper=360.0 * thread_turns)
thread_solid = Pos(outer_radius - thread_depth / 2.0, 0, 0) * thread_bp.part
result = result - thread_solid

keyway_solid = Pos(inner_radius + keyway_depth / 2.0, 0, 0) * Box(keyway_width, keyway_depth, coupler_length)
keyway_solid = chamfer(keyway_solid.edges(), chamfer_size)
result = result - keyway_solid

result = result - Pos(mount_hole_offset, 0, -coupler_length / 2) * Cylinder(mount_hole_diameter / 2, coupler_length)

part = result
part.name = "coupler"
export_step(part, "output.step")