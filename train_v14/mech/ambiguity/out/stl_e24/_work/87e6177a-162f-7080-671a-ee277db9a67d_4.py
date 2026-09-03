from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
length = 60.0
rib_height = 10.0
rib_thickness = 2.0
rib_spacing = 15.0
vent_slot_width = 2.0
vent_slot_height = 12.0
vent_slot_spacing = 10.0
vent_slot_count = 6
chamfer_size = 1.0
pocket_depth = 3.0
pocket_diameter = 30.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib_count = int(length // rib_spacing)
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_thickness/2, 0, rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
    solid_body = solid_body + rib

for i in range(vent_slot_count):
    angle = i * 360.0 / vent_slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - wall_thickness/2, 0, wall_thickness) * Box(vent_slot_width, vent_slot_height, wall_thickness * 2)
    solid_body = solid_body - slot

pocket = Pos(0, 0, length - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)
solid_body = solid_body - pocket

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_ribs_and_vents"
export_step(part, "output.step")