from build123d import *

arm_length = 70.0
base_radius = 10.0
top_radius = 5.0
base_height = 10.0
rib_width = 4.0
rib_height = 12.0
rib_thickness = 3.0
rib_count = 3
hole_diameter = 4.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(arm_length)) as s2:
        Circle(top_radius)
    loft()

arm = p.part
base = Pos(0, 0, base_height / 2) * Cylinder(base_radius, base_height)
result = arm + base

rib = Pos(base_radius, 0, arm_length / 2) * Box(rib_width, rib_height, arm_length)
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    result = result + Rot(0, 0, angle) * rib

result = result - Pos(0, 0, arm_length / 2) * Cylinder(hole_diameter / 2, arm_length + base_height + 10)

top_edges = result.edges().sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_distance)

part = result
part.name = "lofted_arm_with_ribs"
export_step(part, "output.step")