from build123d import *

leg_long = 80.0
leg_short = 60.0
thickness = 10.0
pocket_width = 20.0
pocket_depth = 6.0
pocket_offset = 15.0
counterbore_diameter = 8.0
counterbore_depth = 4.0
through_hole_diameter = 4.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_long, 0), (leg_long, thickness), (thickness, thickness), (thickness, leg_short + thickness), (0, leg_short + thickness), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

pocket_center_x = leg_long - pocket_offset
pocket_center_y = thickness / 2
pocket = Pos(pocket_center_x, pocket_center_y, thickness - pocket_depth / 2) * Box(pocket_width, pocket_depth, pocket_depth)
solid_body = solid_body - pocket

cb_x = thickness / 2
cb_y = leg_short / 2 + thickness
cbore = Pos(cb_x, cb_y, thickness - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)
solid_body = solid_body - cbore
thru = Pos(cb_x, cb_y, thickness / 2) * Cylinder(through_hole_diameter / 2, thickness + 10)
solid_body = solid_body - thru

for i in range(2):
    hx = leg_long / 2 + (i - 0.5) * mount_hole_spacing
    hy = 0
    hole = Pos(hx, hy, thickness / 2) * Cylinder(mount_hole_diameter / 2, thickness + 10)
    solid_body = solid_body - hole

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - thickness) < 1e-3 and abs(e.center().Y - thickness) < 1e-3]
solid_body = fillet(inner_edges, fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")