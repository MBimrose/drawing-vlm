from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
height = 60.0
pocket_diameter = 30.0
pocket_depth = 8.0
vent_slot_width = 6.0
vent_slot_height = 12.0
vent_slot_count = 8
chamfer_size = 1.0
rib_thickness = 2.0
rib_height = 10.0
rib_spacing_angle = 60.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
pocket_radius = pocket_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, height))
            l2 = Line(l1@1, (inner_radius, height))
            l3 = Line(l2@1, (inner_radius, 0))
            l4 = Line(l3@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, height - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)

for i in range(vent_slot_count):
    angle = i * 360.0 / vent_slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - wall_thickness/2.0, 0, 0) * Box(wall_thickness + 0.5, vent_slot_width, vent_slot_height)
    solid_body = solid_body - slot

rib_count = int(360 / rib_spacing_angle)
for i in range(rib_count):
    angle = i * rib_spacing_angle
    rib = Rot(0, 0, angle) * Pos(inner_radius - rib_thickness/2.0, 0, rib_height/2.0) * Box(rib_thickness, rib_thickness, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "hollow_cylinder_with_vents_and_ribs"
export_step(part, "output.step")