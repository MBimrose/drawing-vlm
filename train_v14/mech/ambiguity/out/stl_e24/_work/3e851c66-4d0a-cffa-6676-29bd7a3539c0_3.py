from build123d import *

leg_length = 80.0
leg_height = 60.0
thickness = 6.0
depth = 30.0
inner_fillet_radius = 10.0
hole_diameter = 8.0
gusset_thickness = 4.0
gusset_width = 20.0
gusset_height = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness), (thickness, thickness), (thickness, leg_height), (0, leg_height), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

solid_body = solid_body - Pos(leg_length/2, thickness/2, 0) * Cylinder(hole_diameter/2, depth)
solid_body = solid_body - Pos(thickness/2, leg_height/2, 0) * Cylinder(hole_diameter/2, depth)

with BuildPart() as g:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((0, 0), (gusset_width, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=gusset_thickness)

gusset_body = Pos(thickness/2, thickness/2, depth/2 - gusset_thickness/2) * g.part
solid_body = solid_body + gusset_body

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")