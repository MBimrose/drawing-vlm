from build123d import *
import math

outer_radius = 30.0
inner_radius = 8.0
step_radius = 20.0
height = 40.0
step_height = 10.0
bevel_chamfer = 1.0
blind_hole_radius = 4.0
blind_hole_depth = 25.0
tapped_hole_dia = 5.0
tapped_hole_depth = 30.0
tapped_hole_count = 6
tapped_hole_circle_radius = 15.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((outer_radius, 0), (outer_radius, height - step_height),
                     (step_radius, height - step_height), (step_radius, height),
                     (inner_radius, height), (inner_radius, 0), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid = p.part
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = chamfer(top_face.edges(), bevel_chamfer)

solid = solid - Pos(0, 0, height - blind_hole_depth/2) * Cylinder(blind_hole_radius, blind_hole_depth)

for i in range(tapped_hole_count):
    angle = math.radians(i * 360.0 / tapped_hole_count)
    px = tapped_hole_circle_radius * math.cos(angle)
    py = tapped_hole_circle_radius * math.sin(angle)
    solid = solid - Pos(px, py, height - tapped_hole_depth/2) * Cylinder(tapped_hole_dia/2, tapped_hole_depth)

part = solid
part.name = "stepped_cylinder_with_holes"
export_step(part, OUTPUT_PATH)