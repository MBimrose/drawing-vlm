from build123d import *
import math

outer_radius = 40
shell_thickness = 4
lip_height = 8
shell_height = 30
lip_extension = 6
vent_width = 10
vent_height = 4
vent_count = 6
vent_angle = 360 / vent_count
chamfer_distance = 0.5

inner_radius = outer_radius - shell_thickness

with BuildPart() as p_outer:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as line:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, shell_height - lip_height))
            a1 = ThreePointArc(l2@1, (outer_radius + lip_extension, shell_height - lip_height / 2), (outer_radius + lip_extension, shell_height))
            l3 = Line(a1@1, (outer_radius + lip_extension, 0))
            l4 = Line(l3@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

with BuildPart() as p_inner:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as line:
            l1 = Line((0, 0), (inner_radius, 0))
            l2 = Line(l1@1, (inner_radius, shell_height - lip_height))
            l3 = Line(l2@1, (0, shell_height - lip_height))
            l4 = Line(l3@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p_outer.part - p_inner.part

vent_x = outer_radius + lip_extension / 2
vent_z = (lip_extension + shell_thickness * 2) / 2
vent_h = lip_extension + shell_thickness * 2

for i in range(vent_count):
    angle_deg = i * vent_angle
    vent = Rot(0, 0, angle_deg) * Pos(vent_x, 0, vent_z) * Box(vent_width, vent_height, vent_h)
    solid_body = solid_body - vent

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "shell_with_lip_and_vents"
export_step(part, OUTPUT_PATH)