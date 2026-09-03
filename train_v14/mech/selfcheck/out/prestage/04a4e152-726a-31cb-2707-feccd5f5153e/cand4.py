from build123d import *

jaw_length = 50
jaw_width = 30
jaw_thickness = 12
notch_width = 10
notch_depth = 10
relief_drop = 5
hole_diameter = 6
hole_depth = 8
hole_offset_x = 5
hole_offset_y = 5
chamfer_size = 0.5
pocket1_x = 5
pocket1_y = 5
pocket1_w = 6
pocket1_h = 8
pocket2_x = 25
pocket2_y = 5
pocket2_w = 5
pocket2_h = 6

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (jaw_length, 0), (jaw_length, jaw_width - notch_depth),
                     (notch_width, jaw_width - notch_depth - relief_drop),
                     (notch_width, jaw_width), (0, jaw_width), close=True)
        make_face()
    extrude(amount=jaw_thickness)

solid = p.part

solid = solid - Pos(hole_offset_x, jaw_width - hole_offset_y, jaw_thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

solid = solid - Pos(pocket1_x, pocket1_y, jaw_thickness - jaw_thickness/4) * Box(pocket1_w, pocket1_h, jaw_thickness/2)

solid = solid - Pos(pocket2_x, pocket2_y, jaw_thickness - jaw_thickness/4) * Box(pocket2_w, pocket2_h, jaw_thickness/2)

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

part = solid
part.name = "jaw_with_notch_and_pockets"
export_step(part, "output.step")