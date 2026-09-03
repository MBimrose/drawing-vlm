from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
thickness = 12.0
fillet_radius = 2.0
clearance_hole_diameter = 6.0
mount_hole_diameter = 5.0
mount_hole_spacing = 20.0
mount_hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (thickness, vertical_leg_length),
                     (thickness, thickness), (horizontal_leg_length, thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, fillet_radius)

solid_body = solid_body - Pos(horizontal_leg_length/2, thickness/2, thickness/2) * Cylinder(clearance_hole_diameter/2, thickness)

for i in range(3):
    y = mount_hole_offset + i * mount_hole_spacing
    solid_body = solid_body - Pos(thickness/2, y, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")