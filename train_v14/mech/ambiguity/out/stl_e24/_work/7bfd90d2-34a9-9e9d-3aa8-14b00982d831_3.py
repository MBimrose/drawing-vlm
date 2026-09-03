from build123d import *
import math

knob_outer_radius = 30.0
knob_height = 20.0
shaft_radius = 8.0
wall_thickness = 2.0
pocket_width = 12.0
pocket_height = 8.0
pocket_depth = 4.0
chamfer_size = 1.0
hole_diameter = 4.0
hole_spacing = 12.0
hole_count = 3

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((shaft_radius, 0), (shaft_radius, knob_height))
            l2 = Line(l1@1, (knob_outer_radius, knob_height))
            l3 = Line(l2@1, (knob_outer_radius, 0))
            l4 = Line(l3@1, (shaft_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

pocket_box = Pos(knob_outer_radius - pocket_depth/2, 0, knob_height/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket_box

for i in range(hole_count):
    angle_deg = i * 360.0 / hole_count
    angle_rad = math.radians(angle_deg)
    px = (knob_outer_radius - wall_thickness/2) * math.cos(angle_rad)
    py = (knob_outer_radius - wall_thickness/2) * math.sin(angle_rad)
    hole = Pos(px, py, knob_height/2) * Rot(0, 0, angle_deg) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, wall_thickness*2)
    solid_body = solid_body - hole

part = solid_body
part.name = "knob"
export_step(part, "output.step")