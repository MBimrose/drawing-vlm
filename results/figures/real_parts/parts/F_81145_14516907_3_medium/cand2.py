from build123d import *
import math

outer_diameter = 80.0
flange_thickness = 5.0
hub_diameter = 30.0
hub_length = 15.0
shaft_diameter = 15.0
shaft_length = 40.0
slot_width = 10.0
slot_depth = 20.0
chamfer_size = 1.0
clearance = 0.2

outer_radius = outer_diameter / 2.0
hub_radius = hub_diameter / 2.0
shaft_radius = shaft_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, flange_thickness))
            l3 = Line(l2 @ 1, (hub_radius, flange_thickness))
            l4 = Line(l3 @ 1, (hub_radius, flange_thickness + hub_length))
            l5 = Line(l4 @ 1, (shaft_radius, flange_thickness + hub_length))
            l6 = Line(l5 @ 1, (shaft_radius, flange_thickness + hub_length + shaft_length))
            l7 = Line(l6 @ 1, (0, flange_thickness + hub_length + shaft_length))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Y)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

slot_center_radius = outer_radius - slot_depth / 2.0
for i in range(4):
    angle = math.radians(i * 90)
    px = slot_center_radius * math.cos(angle)
    pz = slot_center_radius * math.sin(angle)
    slot = Pos(px, flange_thickness / 2.0, pz) * Box(slot_depth, flange_thickness, slot_width)
    solid_body = solid_body - slot

part = solid_body
part.name = "revolved_shaft_with_slots"
export_step(part, "output.step")