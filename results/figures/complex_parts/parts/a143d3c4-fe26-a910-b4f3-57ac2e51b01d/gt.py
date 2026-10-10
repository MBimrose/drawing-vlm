from build123d import *
import math

small_bore_diameter = 20.0
wall_thickness = 5.0
hub_length = 40.0
outer_flange_diameter = 80.0
flange_thickness = 8.0
bolt_hole_diameter = 5.0
bolt_circle_diameter = 60.0
number_of_bolts = 6
chamfer_size = 1.0
slot_width = 6.0

inner_radius_small = small_bore_diameter / 2.0
outer_radius_small = inner_radius_small + wall_thickness
outer_radius_top = outer_flange_diameter / 2.0
bolt_circle_radius = bolt_circle_diameter / 2.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(outer_radius_small)
        Circle(inner_radius_small)
    with BuildSketch(Plane.XY.offset(hub_length)) as s2:
        Circle(outer_radius_top)
        Circle(inner_radius_small)
    loft()
    with BuildSketch(Plane.XY.offset(hub_length)) as s3:
        Circle(outer_radius_top)
    extrude(amount=flange_thickness)

solid_body = p.part
solid_body = solid_body + Pos(outer_radius_small - slot_width / 2.0, 0, hub_length / 2.0) * Box(slot_width, hub_length, hub_length)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

for i in range(number_of_bolts):
    angle = math.radians(i * 360.0 / number_of_bolts)
    px = bolt_circle_radius * math.cos(angle)
    py = bolt_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, hub_length + flange_thickness / 2.0) * Cylinder(bolt_hole_diameter / 2.0, hub_length + flange_thickness + 10.0)

part = solid_body
part.name = "hub_adapter"
export_step(part, OUTPUT_PATH)