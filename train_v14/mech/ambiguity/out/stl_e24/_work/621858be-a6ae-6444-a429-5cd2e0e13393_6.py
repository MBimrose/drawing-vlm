from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 6.0
height = 30.0
rib_height = 5.0
rib_width = 4.0
rib_count = 8
slot_width = 4.0
slot_height = 12.0
slot_depth = wall_thickness + 2.0
slot_count = 6
chamfer_size = 1.0
fillet_radius = 2.0
pocket_diameter = 20.0
pocket_depth = 4.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
rib_outer_radius = outer_radius + rib_width

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, height))
            l2 = Line(l1@1, (rib_outer_radius, height))
            l3 = Line(l2@1, (rib_outer_radius, 0))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = fillet(bottom_face.edges(), fillet_radius)

solid_body = solid_body - Pos(0, 0, height - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)

slot_radius = outer_radius + rib_width - slot_depth / 2.0
for i in range(slot_count):
    angle_deg = i * 360.0 / slot_count
    angle_rad = math.radians(angle_deg)
    px = slot_radius * math.cos(angle_rad)
    py = slot_radius * math.sin(angle_rad)
    slot = Pos(px, py, (height - slot_height)/2) * Rot(0, 0, angle_deg) * Box(slot_depth, slot_width, slot_height)
    solid_body = solid_body - slot

part = solid_body
part.name = "revolved_cup_with_slots"
export_step(part, "output.step")