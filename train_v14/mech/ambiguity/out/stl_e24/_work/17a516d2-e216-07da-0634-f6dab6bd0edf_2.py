from build123d import *

leg_length = 70.0
leg_height = 60.0
thickness = 8.0
extrude_depth = 12.0
hole_diameter = 6.0
chamfer_size = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness),
                     (thickness, thickness), (thickness, leg_height),
                     (0, leg_height), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part

# Chamfer inner corner edge at (thickness, thickness)
inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = chamfer(inner_edges, chamfer_size)

# Horizontal leg hole
solid_body = solid_body - Pos(leg_length/2, thickness/2, extrude_depth/2) * Cylinder(hole_diameter/2, extrude_depth)

# Vertical leg hole
solid_body = solid_body - Pos(thickness/2, leg_height/2, extrude_depth/2) * Cylinder(hole_diameter/2, extrude_depth)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")