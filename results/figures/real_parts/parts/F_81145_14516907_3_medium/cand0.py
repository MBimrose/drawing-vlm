from build123d import *

outer_diameter = 80.0
flange_thickness = 5.0
hub_diameter = 30.0
hub_length = 20.0
shaft_diameter = 15.0
shaft_length = 40.0
rib_width = 10.0
rib_height = 12.0
rib_thickness = 3.0
chamfer_size = 1.0

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

top_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

rib = Pos(outer_radius - rib_thickness / 2.0, flange_thickness / 2.0, 0) * Box(rib_thickness, rib_width, rib_height)

ribs = rib
for i in range(1, 4):
    ribs = ribs + Rot(0, i * 90, 0) * rib

part = solid_body + ribs
part.name = "flange_with_ribs"
export_step(part, "output.step")