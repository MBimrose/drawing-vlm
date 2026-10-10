from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
plate_thickness = 5.0
arm_width = 12.0
arm_length = (outer_diameter - inner_diameter) / 2.0
hole_diameter = 5.0
hole_clearance = 0.2
chamfer_angle_deg = 20.0
chamfer_distance = plate_thickness * math.tan(math.radians(chamfer_angle_deg))
pocket_diameter = 30.0
pocket_depth = 2.0

central = Cylinder(inner_diameter / 2.0, plate_thickness)
arm = Pos(inner_diameter / 2.0 + arm_length / 2.0, 0, 0) * Box(arm_length, arm_width, plate_thickness)
arms = arm
for angle in [90, 180, 270]:
    arms = arms + Rot(0, 0, angle) * arm
result = central + arms

result = result - Cylinder((hole_diameter + hole_clearance) / 2.0, plate_thickness)

hole_center_radius = inner_diameter / 2.0 + arm_length / 2.0
for i in range(4):
    angle = math.radians(i * 90)
    px = hole_center_radius * math.cos(angle)
    py = hole_center_radius * math.sin(angle)
    result = result - Pos(px, py, 0) * Cylinder((hole_diameter + hole_clearance) / 2.0, plate_thickness)

result = result - Pos(0, 0, plate_thickness - pocket_depth / 2.0) * Cylinder(pocket_diameter / 2.0, pocket_depth)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "cross_plate"
export_step(part, "output.step")