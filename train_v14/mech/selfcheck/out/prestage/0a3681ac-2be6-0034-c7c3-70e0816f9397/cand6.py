from build123d import *

bracket_width = 70.0
bracket_depth = 30.0
bracket_thickness = 8.0
rib_height = 6.0
rib_base = 10.0
rib_thickness = bracket_thickness
pocket_width = 20.0
pocket_depth = 6.0
pocket_cut_depth = 4.0
hole_diameter = 8.0
hole_offset_x = 15.0
fillet_radius = 1.0

base = Box(bracket_width, bracket_depth, bracket_thickness)

with BuildPart() as rib_bp:
    with BuildSketch(Plane.XZ.offset(-bracket_depth/2)) as sk:
        with BuildLine() as bl:
            Polyline((-rib_base/2, 0), (rib_base/2, 0), (0, rib_height), close=True)
        make_face()
    extrude(amount=rib_thickness)
rib = rib_bp.part

result = base + rib

pocket = Pos(0, bracket_depth/2 - pocket_depth/2, -bracket_thickness/2 + pocket_cut_depth/2) * Box(pocket_width, pocket_depth, pocket_cut_depth)
result = result - pocket

hole = Pos(hole_offset_x, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness + 10)
result = result - hole

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "bracket_with_rib"
export_step(part, "output.step")