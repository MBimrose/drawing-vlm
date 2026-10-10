from build123d import *

leg_length = 80.0
leg_width = 20.0
thickness = 8.0
inner_fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_offset_from_inner = 15.0
cbore_diameter = 8.0
cbore_depth = 3.0
rib_thickness = 2.0
rib_height = 6.0
pocket_width = 12.0
pocket_depth = 4.0
pocket_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness), (thickness, thickness), (thickness, leg_length), (0, leg_length), close=True)
        make_face()
    extrude(amount=leg_width)

solid_body = p.part

inner_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[1:2]
solid_body = fillet(inner_edges, inner_fillet_radius)

for x, y in [(hole_offset_from_inner + hole_spacing/2, thickness/2),
             (hole_offset_from_inner + 1.5*hole_spacing, thickness/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, leg_width + 1)
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(cbore_diameter/2, cbore_depth)

rib = Pos(rib_thickness/2, leg_length/2, leg_width/2) * Box(rib_thickness, leg_length, rib_height)
solid_body = solid_body + rib

pocket = Pos(pocket_offset + pocket_width/2, thickness/2, leg_width - pocket_depth/2) * Box(pocket_width, pocket_depth, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")