from build123d import *
import math

knob_outer_radius = 30.0
knob_height = 12.0
knob_shaft_radius = 8.0
shaft_length = 20.0
shaft_overlap = 2.0
vent_hole_radius = 2.0
vent_hole_count = 12
vent_hole_margin = 4.0
chamfer_distance = 0.8

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (knob_outer_radius, 0))
            l2 = Line(l1@1, (knob_outer_radius, knob_height - 2))
            arc = ThreePointArc(l2@1, (knob_outer_radius - 2, knob_height), (knob_outer_radius - 4, knob_height))
            l3 = Line(arc@1, (0, knob_height))
            l4 = Line(l3@1, l1@0)
        make_face()
    revolve(axis=Axis.Z)

solid = p.part

solid = solid - Pos(0, 0, knob_height/2) * Cylinder(radius=knob_shaft_radius, height=knob_height + 1)

shaft = Pos(0, 0, knob_height - shaft_overlap + shaft_length/2) * Cylinder(radius=knob_shaft_radius, height=shaft_length)
solid = solid + shaft

for i in range(vent_hole_count):
    angle = math.radians(i * 360.0 / vent_hole_count)
    x = (knob_outer_radius - vent_hole_margin) * math.cos(angle)
    y = (knob_outer_radius - vent_hole_margin) * math.sin(angle)
    hole = Pos(x, y, knob_height/2) * Cylinder(radius=vent_hole_radius, height=knob_height + 1)
    solid = solid - hole

top_edges = solid.edges().sort_by(Axis.Z)[-1:]
solid = chamfer(solid, top_edges, chamfer_distance)

part = solid
part.name = "knob_with_shaft_and_vents"
export_step(part, OUTPUT_PATH)