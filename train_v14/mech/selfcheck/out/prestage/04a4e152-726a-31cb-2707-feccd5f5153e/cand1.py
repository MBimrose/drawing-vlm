from build123d import *

leg_length = 50.0
leg_height = 30.0
thickness = 10.0
depth = 12.0
relief_offset = 10.0
relief_length = 40.0
relief_depth = 4.0
relief_angle = 4.0
blind_hole_diameter = 6.0
blind_hole_depth = 8.0
chamfer_size = 0.5
pocket_width = 6.0
pocket_height = 5.0
pocket_depth = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length, 0), (leg_length, thickness), (thickness, thickness), (thickness, leg_height), (0, leg_height), close=True)
        make_face()
    extrude(amount=depth)
base = p.part

with BuildPart() as rp:
    with BuildSketch() as rsk:
        with BuildLine() as rbl:
            Polyline((relief_offset, thickness), (relief_offset + relief_length, thickness), (relief_offset + relief_length, thickness - relief_depth), (relief_offset, thickness - relief_depth), close=True)
        make_face()
    extrude(amount=depth)
relief_cut = rp.part

result = base - relief_cut

hole_center_x = thickness / 2
hole_center_y = leg_height - 5.0
result = result - Pos(hole_center_x, hole_center_y, depth - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

result = result - Pos(leg_length/2, thickness/2, depth - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
result = result - Pos(thickness/2, leg_height/2, depth - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)

part = result
part.name = "L_bracket_with_relief_and_pockets"
export_step(part, "output.step")