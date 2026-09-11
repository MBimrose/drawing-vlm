from build123d import *

bracket_length = 80.0
bracket_height = 35.0
bracket_thickness = 8.0
wall_thickness = 0.8
fillet_radius = 3.0
hole_diameter = 3.4
hole_spacing = 12.0
hole_rows = 2
hole_cols = 2
hole_offset_x = 15.0
hole_offset_y = 10.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 2.0
slot_width = 6.0
slot_length = 20.0
slot_offset_x = 10.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((-bracket_length/2 + bracket_height/2, -bracket_height/2),
                       (bracket_length/2 - bracket_height/2, -bracket_height/2))
            a1 = ThreePointArc(l1 @ 1, (bracket_length/2, 0),
                               (bracket_length/2 - bracket_height/2, bracket_height/2))
            l2 = Line(a1 @ 1, (-bracket_length/2 + bracket_height/2, bracket_height/2))
            a2 = ThreePointArc(l2 @ 1, (-bracket_length/2, 0),
                               (-bracket_length/2 + bracket_height/2, -bracket_height/2))
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)
solid_body = offset(solid_body, amount=-wall_thickness)

pocket = Pos(0, bracket_thickness - pocket_depth/2, 0) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

slot = Pos(bracket_length/2 - slot_offset_x, bracket_thickness/2, 0) * Box(slot_width, bracket_thickness, slot_length)
solid_body = solid_body - slot

for i in range(hole_cols):
    for j in range(hole_rows):
        hx = -bracket_length/2 + hole_offset_x + (i - (hole_cols-1)/2) * hole_spacing
        hz = -bracket_height/2 + hole_offset_y + (j - (hole_rows-1)/2) * hole_spacing
        hole = Pos(hx, bracket_thickness/2, hz) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness)
        solid_body = solid_body - hole

part = solid_body
part.name = "bracket"
export_step(part, "output.step")