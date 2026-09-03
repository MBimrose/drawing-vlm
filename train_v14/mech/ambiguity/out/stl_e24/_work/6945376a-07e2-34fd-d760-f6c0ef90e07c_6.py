from build123d import *

leg_length = 80.0
leg_height = 60.0
leg_thickness = 12.0
bracket_thickness = 8.0
rib_width = 8.0
rib_height = 6.0
rib_thickness = 4.0
hole_diameter = 4.5
hole_spacing = 20.0
hole_offset = 15.0
fillet_radius = 2.0
pocket_width = 20.0
pocket_height = 6.0
pocket_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_height),
                     (leg_length - leg_thickness, leg_height),
                     (leg_length - leg_thickness, leg_thickness),
                     (0, leg_thickness), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

rib = Pos(leg_thickness/2, leg_thickness/2, bracket_thickness + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

hole_r = hole_diameter / 2
for y in [leg_height/2 - hole_spacing/2, leg_height/2, leg_height/2 + hole_spacing/2]:
    solid_body = solid_body - Pos(leg_length - leg_thickness/2, y, bracket_thickness/2) * Cylinder(hole_r, bracket_thickness + 2)

pocket = Pos(leg_length - leg_thickness/2, leg_height/2, bracket_thickness - pocket_depth/2) * Box(pocket_height, pocket_width, pocket_depth)
solid_body = solid_body - pocket

inner_edges = [e for e in solid_body.edges() if abs(e.center().X) < 1e-3 and abs(e.center().Y) < 1e-3]
solid_body = fillet(inner_edges, fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")