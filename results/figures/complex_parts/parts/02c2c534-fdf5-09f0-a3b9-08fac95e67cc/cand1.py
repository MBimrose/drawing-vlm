from build123d import *

arm_length = 70.0
base_radius = 12.0
mid_radius = 8.0
tip_radius = 4.0
hub_radius = 10.0
hub_thickness = 10.0
hole_diameter = 4.0
slot_width = 2.0
slot_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(arm_length * 0.4)) as s2:
        Circle(mid_radius)
    with BuildSketch(Plane.XY.offset(arm_length)) as s3:
        Circle(tip_radius)
    loft()
arm = p.part

hub = Pos(0, 0, hub_thickness / 2) * Cylinder(hub_radius, hub_thickness)
combined = arm + hub

hole = Pos(0, 0, (arm_length + hub_thickness) / 2) * Cylinder(hole_diameter / 2, arm_length + hub_thickness)
combined = combined - hole

slot = Pos(0, 0, arm_length / 2) * Box(slot_width, slot_depth, arm_length)
result = combined - slot

part = result
part.name = "lofted_arm_with_hub"
export_step(part, "output.step")