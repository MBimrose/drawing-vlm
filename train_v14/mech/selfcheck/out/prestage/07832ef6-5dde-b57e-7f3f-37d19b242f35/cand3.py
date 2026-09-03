from build123d import *
import math

shank_radius = 8.0
shank_length = 60.0
head_radius = 38.0
head_height = 20.0
hole_diameter = 5.0
hole_depth = 10.0
hole_pattern_radius = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (shank_radius, 0), (shank_radius, shank_length),
                     (head_radius, shank_length), (head_radius, shank_length + head_height),
                     (0, shank_length + head_height), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_z = shank_length + head_height

for i in range(4):
    angle = math.radians(i * 90)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, top_z - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

part = solid_body
part.name = "revolved_pin_with_holes"
export_step(part, "output.step")