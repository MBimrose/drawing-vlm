from build123d import *

chute_length = 90.0
chute_width = 40.0
chute_height = 30.0
wall_thickness = 3.0
rib_height = 12.0
rib_base = 10.0
rib_offset = 5.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_from_end = 20.0

base = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

with BuildPart() as rib_bp:
    with BuildSketch(Plane.XZ.offset(-chute_width/2)) as sk:
        with BuildLine() as bl:
            Polyline((rib_offset, chute_height/2 - rib_height/2),
                     (rib_offset + rib_base, chute_height/2),
                     (rib_offset, chute_height/2 + rib_height/2), close=True)
        make_face()
    extrude(amount=wall_thickness)
rib = rib_bp.part

result = base + rib

hole = Pos(-chute_length/2 + hole_offset_from_end, -chute_width/2, chute_height) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, chute_width)
result = result - hole

bottom_face = result.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
result = fillet(bottom_edges, fillet_radius)

part = result
part.name = "chute"
export_step(part, "output.step")