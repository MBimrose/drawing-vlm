from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
ring_thickness = 10.0
wall_thickness = 3.0
slot_width = 5.0
slot_length = 20.0
slot_depth = ring_thickness
chamfer_distance = 0.5
central_hole_diameter = 8.0
rib_width = 6.0
rib_height = 4.0
rib_offset = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2)
    extrude(amount=ring_thickness)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness)

solid_body = solid_body - Pos(0, 0, ring_thickness / 2) * Cylinder(central_hole_diameter / 2, ring_thickness)

slot_box = Pos(outer_diameter / 2 - wall_thickness / 2, 0, ring_thickness / 2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot_box

z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges, chamfer_distance)

rib = Pos(outer_diameter / 2 - rib_offset, 0, ring_thickness / 2) * Box(rib_width, rib_height, ring_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "shelled_ring_with_slot_and_rib"
export_step(part, "output.step")