from build123d import *

leg_length = 60.0
leg_width = 20.0
thickness = 10.0
rib_height = 20.0
rib_width = 4.0
rib_thickness = 2.0
hole_diameter = 4.0
hole_offset = 10.0
fillet_radius = 1.5
pocket_depth = 1.0
pocket_width = 12.0
pocket_height = 12.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width), (leg_width, leg_width), (leg_width, leg_length), (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

# Fillet inner corner edge (|Z and >X and >Y)
z_edges = solid_body.edges().filter_by(Axis.Z)
inner_edge = max(z_edges, key=lambda e: (e.center().X, e.center().Y))
solid_body = fillet([inner_edge], fillet_radius)

# Rib on >X face
rib_x = Pos(leg_length + rib_thickness/2, leg_width/2, thickness/2) * Box(rib_thickness, rib_width, rib_height)
solid_body = solid_body + rib_x

# Rib on >Y face
rib_y = Pos(leg_width/2, leg_length + rib_thickness/2, thickness/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib_y

# Hole on >X face
hole_x = Pos(leg_length, hole_offset, thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, leg_length * 2)
solid_body = solid_body - hole_x

# Pocket on >Z face
pocket = Pos(leg_width/2, leg_width/2, thickness - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "L_bracket_with_ribs"
export_step(part, "output.step")