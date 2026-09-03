from build123d import *

outer_diameter = 60.0
wall_thickness = 5.0
length = 30.0
slot_width = 4.0
slot_length = 10.0
num_slots = 12
chamfer_size = 2.0
central_hole_diameter = 20.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

solid_body = solid_body - Cylinder(central_hole_diameter / 2, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

for i in range(num_slots):
    angle = i * 360.0 / num_slots
    slot = Rot(0, 0, angle) * Pos(outer_radius - wall_thickness / 2.0, 0, length / 2.0) * Box(wall_thickness + 0.2, slot_width, slot_length)
    solid_body = solid_body - slot

part = solid_body
part.name = "hollow_cylinder_with_slots"
export_step(part, "output.step")