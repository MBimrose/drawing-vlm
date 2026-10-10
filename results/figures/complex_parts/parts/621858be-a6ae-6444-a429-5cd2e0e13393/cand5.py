from build123d import *
import math

outer_radius = 45
wall_thickness = 5
height = 30
rib_thickness = 2
rib_height = 5
slot_width = 4
slot_count = 6
chamfer_size = 2
mount_hole_diameter = 5
mount_hole_count = 4
central_hole_diameter = 8

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius + wall_thickness, 0), (outer_radius + wall_thickness, height))
            l2 = Line(l1@1, (outer_radius, height))
            l3 = Line(l2@1, (outer_radius, 0))
            l4 = Line(l3@1, (outer_radius + wall_thickness, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

rib = Pos(0, 0, height/2) * (Cylinder(outer_radius + rib_thickness, rib_height) - Cylinder(outer_radius, rib_height))
solid_body = solid_body + rib

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius + wall_thickness/2, 0, 0) * Box(wall_thickness + 0.2, slot_width, height)
    solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Cylinder(central_hole_diameter/2, height + 10)

for i in range(mount_hole_count):
    angle = i * 360.0 / mount_hole_count
    hole = Rot(0, 0, angle) * Pos(outer_radius + wall_thickness/2, 0, height/2) * Cylinder(mount_hole_diameter/2, wall_thickness + 0.5)
    solid_body = solid_body - hole

part = solid_body
part.name = "revolved_ring_with_ribs_slots"
export_step(part, "output.step")