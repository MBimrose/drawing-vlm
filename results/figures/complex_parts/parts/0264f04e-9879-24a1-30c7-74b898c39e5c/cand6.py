from build123d import *

outer_radius = 30.0
step_radius = 20.0
shaft_radius = 12.0
base_height = 15.0
step_height = 15.0
shaft_height = 20.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 40.0
slot_width = 6.0
slot_depth = 4.0

total_height = base_height + step_height + shaft_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, base_height))
            l3 = Line(l2 @ 1, (step_radius, base_height))
            l4 = Line(l3 @ 1, (step_radius, base_height + step_height))
            l5 = Line(l4 @ 1, (shaft_radius, base_height + step_height))
            l6 = Line(l5 @ 1, (shaft_radius, total_height))
            l7 = Line(l6 @ 1, (0, total_height))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

internal_edges = [e for e in solid_body.edges() if abs(e.center().Z - base_height) < 1e-3 or abs(e.center().Z - (base_height + step_height)) < 1e-3]
solid_body = fillet(internal_edges, fillet_radius)

for y in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(0, y, total_height/2) * Cylinder(hole_diameter/2, total_height + 10)

slot_box = Pos(shaft_radius - slot_depth/2, 0, total_height - slot_depth/2) * Box(slot_width, slot_depth, slot_depth)
solid_body = solid_body - slot_box

part = solid_body
part.name = "stepped_shaft_with_holes_and_slot"
export_step(part, "output.step")