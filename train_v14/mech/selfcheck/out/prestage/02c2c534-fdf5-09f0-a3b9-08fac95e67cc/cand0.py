from build123d import *

base_radius = 10.0
base_height = 10.0
arm_length = 70.0
arm_start_radius = 12.0
arm_end_radius = 5.0
twist_degrees = 360.0
hole_diameter = 4.0
chamfer_size = 0.5

base = Pos(0, 0, base_height/2) * Cylinder(base_radius, base_height)

with BuildPart() as p:
    with BuildSketch(Plane.XY.offset(base_height)) as s1:
        Circle(arm_start_radius)
    with BuildSketch(Plane.XY.offset(arm_length/2)) as s2:
        Circle((arm_start_radius + arm_end_radius) / 2)
    with BuildSketch(Plane.XY.offset(arm_length)) as s3:
        Circle(arm_end_radius)
    loft()
arm = p.part

result = base + arm
result = result - Pos(0, 0, arm_length/2) * Cylinder(hole_diameter/2, arm_length + 10)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "twisted_arm"
export_step(part, "output.step")