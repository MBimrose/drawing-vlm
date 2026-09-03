from build123d import *

knob_outer_radius = 25.0
knob_height = 30.0
central_hole_radius = 6.0
rib_width = 5.0
rib_thickness = 2.0
rib_height = 20.0
rib_count = 12
chamfer_distance = 1.0

solid_body = Cylinder(knob_outer_radius, knob_height)
solid_body = solid_body - Cylinder(central_hole_radius, knob_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

rib = Pos(knob_outer_radius + rib_thickness/2, 0, rib_height/2) * Box(rib_width, rib_thickness, rib_height)
ribs = rib
for i in range(1, rib_count):
    angle = 360.0 / rib_count * i
    ribs = ribs + Rot(0, 0, angle) * rib

part = solid_body + ribs
part.name = "knob_with_ribs"
export_step(part, "output.step")