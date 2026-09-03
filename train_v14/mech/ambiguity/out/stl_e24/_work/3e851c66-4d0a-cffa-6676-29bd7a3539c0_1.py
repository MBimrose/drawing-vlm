from build123d import *

leg_length = 80.0
leg_width = 60.0
thickness = 6.0
extrude_length = 30.0
inner_fillet_radius = 10.0
hole_diameter = 8.0
rib_length = 12.0
rib_width = 12.0
rib_thickness = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness),
                     (thickness, thickness), (thickness, leg_width),
                     (0, leg_width), close=True)
        make_face()
    extrude(amount=extrude_length)

solid_body = p.part

# Fillet inner corner edge (|Z and >X and >Y)
z_edges = solid_body.edges().filter_by(Axis.Z)
inner_edge = min(z_edges, key=lambda e: (e.center().X - thickness)**2 + (e.center().Y - thickness)**2)
solid_body = fillet([inner_edge], inner_fillet_radius)

# Holes on outer faces
solid_body = solid_body - Pos(leg_length/2, thickness/2, 0) * Cylinder(hole_diameter/2, extrude_length)
solid_body = solid_body - Pos(thickness/2, leg_width/2, 0) * Cylinder(hole_diameter/2, extrude_length)

# Rib on inner face
rib = Pos(thickness/2, thickness/2, extrude_length/2) * Box(rib_length, rib_width, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket_with_rib"
export_step(part, "output.step")