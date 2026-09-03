from build123d import *

leg_length = 80.0
thickness = 4.0
depth = 20.0
rib_width = 6.0
rib_height = 12.0
pocket_width = 20.0
pocket_height = 30.0
pocket_depth = 4.0
hole_diameter = 5.0
cbore_diameter = 8.0
cbore_depth = 2.0
hole_spacing = 30.0
hole_offset = 15.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length,0), (leg_length,thickness), (thickness,thickness), (thickness,leg_length), (0,leg_length), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part

rib = Pos(thickness/2, leg_length + rib_height/2, depth/2) * Box(rib_width, rib_height, rib_width)
solid_body = solid_body + rib

pocket = Pos(pocket_depth/2, leg_length/2, depth/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

for x, y in [(hole_offset, thickness/2), (hole_offset + hole_spacing, thickness/2)]:
    shaft = Pos(x, y, 0) * Cylinder(hole_diameter/2, depth + 1)
    cbore = Pos(x, y, 0) * Cylinder(cbore_diameter/2, cbore_depth)
    solid_body = solid_body - shaft - cbore

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")