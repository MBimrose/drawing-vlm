from build123d import *

leg_length = 70.0
leg_height = 50.0
thickness = 8.0
extrude_depth = 12.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_offset_from_corner = 15.0
pocket_width = 20.0
pocket_height = 15.0
pocket_depth = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness), (thickness, thickness),
                     (thickness, leg_height + thickness), (0, leg_height + thickness), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

pocket = Pos(thickness/2, leg_height + thickness - pocket_depth/2, extrude_depth) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

hole_positions = [
    (thickness + hole_offset_from_corner, thickness/2),
    (thickness + hole_offset_from_corner + hole_spacing, thickness/2),
    (thickness + hole_offset_from_corner + 2*hole_spacing, thickness/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, extrude_depth/2) * Cylinder(hole_diameter/2, extrude_depth)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")