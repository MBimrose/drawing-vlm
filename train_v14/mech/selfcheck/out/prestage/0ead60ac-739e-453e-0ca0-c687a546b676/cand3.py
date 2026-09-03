from build123d import *
import math

length = 80.0
width = 20.0
thickness = 10.0
groove_depth = 2.0
groove_angle = 60.0
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_size = 0.5

half_angle_rad = math.radians(groove_angle / 2.0)
half_width = groove_depth / math.tan(half_angle_rad)

base = Pos(0, 0, thickness / 2) * Box(length, width, thickness)

with BuildPart() as gp:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            Polyline((-half_width, 0), (0, -groove_depth), (half_width, 0), close=True)
        make_face()
    extrude(amount=length)

groove = Pos(-length / 2, 0, thickness) * gp.part
result = base - groove

for x in [-hole_spacing / 2, hole_spacing / 2]:
    result = result - Pos(x, 0, thickness / 2) * Cylinder(hole_diameter / 2, thickness)

result = chamfer(result.edges().filter_by(Axis.X), chamfer_size)

part = result
part.name = "grooved_plate"
export_step(part, "output.step")