from build123d import *

trough_length = 90.0
trough_width = 40.0
trough_height = 30.0
wall_thickness = 3.0
rib_height = 12.0
rib_width = 10.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset = 15.0

base = Pos(0, 0, trough_height / 2) * Box(trough_length, trough_width, trough_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

with BuildPart() as rib_bp:
    with BuildSketch(Plane.XZ.offset(-trough_width / 2)) as sk:
        RegularPolygon(rib_width, 3)
    extrude(amount=wall_thickness)
rib = Pos(0, 0, trough_height / 2) * rib_bp.part

result = base + rib

hole = Pos(-trough_length / 2 + hole_offset, 0, trough_height) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, trough_width)
result = result - hole

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = fillet(bottom_face.edges(), fillet_radius)

part = result
part.name = "trough_with_rib"
export_step(part, "output.step")