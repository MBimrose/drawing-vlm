from build123d import *

leg_length = 80.0
leg_thickness = 8.0
extrude_depth = 20.0
inner_fillet_radius = 2.0
hole_diameter = 5.0
cbore_diameter = 8.0
cbore_depth = 3.0
hole_spacing = 30.0
rib_thickness = 4.0
rib_width = 20.0
rib_height = 6.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_length),
                     (0, leg_length), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

rib = Pos(leg_thickness/2, leg_length + rib_height/2, extrude_depth/2) * Box(rib_thickness, rib_width, rib_height)
solid_body = solid_body + rib

pocket = Pos(leg_thickness/2, leg_thickness/2, extrude_depth - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

for x, y in [(leg_length/2 - hole_spacing/2, leg_thickness/2), (leg_length/2 + hole_spacing/2, leg_thickness/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, extrude_depth + 1)
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(cbore_diameter/2, cbore_depth)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")