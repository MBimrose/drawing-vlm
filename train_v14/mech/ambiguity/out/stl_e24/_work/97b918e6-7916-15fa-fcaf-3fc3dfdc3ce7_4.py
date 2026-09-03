from build123d import *

vertical_height = 80.0
horizontal_length = 60.0
thickness = 12.0
inner_fillet_radius = 3.0
clearance_hole_diameter = 5.0
clearance_hole_spacing = 20.0
clearance_hole_offset = 15.0
mount_hole_diameter = 6.0
mount_hole_offset = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_height), (thickness, vertical_height),
                     (thickness, thickness), (horizontal_length, thickness),
                     (horizontal_length, 0), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - thickness) < 1e-3 and abs(e.center().Y - thickness) < 1e-3]
solid_body = fillet(inner_edges, inner_fillet_radius)

for i in range(3):
    y = clearance_hole_offset + i * clearance_hole_spacing
    solid_body = solid_body - Pos(thickness/2, y, thickness/2) * Cylinder(clearance_hole_diameter/2, thickness)

solid_body = solid_body - Pos(mount_hole_offset, thickness/2, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")