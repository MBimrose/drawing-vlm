from build123d import *

leg_length = 80.0
leg_width = 20.0
thickness = 4.0
rib_height = 20.0
rib_thickness = 6.0
rib_extension = 8.0
hole_diameter = 5.0
cbore_diameter = 8.0
cbore_depth = 3.0
hole_spacing = 30.0
fillet_radius = 2.0
slot_width = 4.0
slot_length = 20.0
slot_depth = 7.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length,0), (leg_length,thickness), (thickness,thickness), (thickness,leg_length), (0,leg_length), close=True)
        make_face()
    extrude(amount=leg_width)

solid_body = p.part

rib = Pos(thickness/2, leg_length + rib_extension/2, leg_width/2) * Box(rib_thickness, rib_extension, rib_height)
solid_body = solid_body + rib

for x in [leg_length/2 - hole_spacing/2, leg_length/2 + hole_spacing/2]:
    solid_body = solid_body - Pos(x, thickness/2, 0) * Cylinder(hole_diameter/2, leg_width + 1)
    solid_body = solid_body - Pos(x, thickness/2, 0) * Cylinder(cbore_diameter/2, cbore_depth)

slot = Pos(thickness/2, leg_length - slot_length/2 - 10, leg_width/2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, fillet_radius)

part = solid_body
part.name = "L_bracket_with_rib"
export_step(part, "output.step")