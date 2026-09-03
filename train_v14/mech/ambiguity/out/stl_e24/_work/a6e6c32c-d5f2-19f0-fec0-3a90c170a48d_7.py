from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 5.0
corner_fillet_radius = 6.0
edge_chamfer = 0.7
rib_height = 3.0
rib_thickness = 2.0
rib_spacing = 12.0
rib_count = 5
hole_diameter = 3.0
hole_cbore_diameter = 5.0
hole_cbore_depth = 2.0
hole_offset_x = 20.0
hole_offset_y = 20.0

solid = Box(plate_width, plate_depth, plate_thickness)
solid = fillet(solid.edges().filter_by(Axis.Z), corner_fillet_radius)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = chamfer(top_face.edges(), edge_chamfer)

for i in range(rib_count):
    y = (i - (rib_count - 1) / 2) * rib_spacing
    solid = solid + Pos(plate_width / 2 + rib_thickness / 2, y, 0) * Box(rib_thickness, rib_thickness, rib_height)

solid = solid - Pos(hole_offset_x, hole_offset_y, plate_thickness / 2) * CounterBoreHole(hole_diameter / 2, hole_cbore_diameter / 2, hole_cbore_depth, plate_thickness)

part = solid
part.name = "plate_with_ribs_and_hole"
export_step(part, "output.step")