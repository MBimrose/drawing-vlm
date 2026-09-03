from build123d import *

plate_width = 80.0
plate_length = 80.0
plate_thickness = 5.0
frame_height = 6.0
frame_thickness = 4.0
hole_diameter = 5.0
hole_spacing = 18.0
hole_rows = 3
hole_cols = 3
chamfer_size = 0.5

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_length, plate_thickness)
frame_outer = Pos(0, 0, plate_thickness + frame_height/2) * Box(plate_width, plate_length, frame_height)
frame_inner = Pos(0, 0, plate_thickness + frame_height/2) * Box(plate_width - 2*frame_thickness, plate_length - 2*frame_thickness, frame_height)
frame = frame_outer - frame_inner
solid_body = base + frame

hole_radius = hole_diameter / 2
hole_depth = plate_thickness + frame_height + 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing
        y = (j - (hole_rows-1)/2) * hole_spacing
        solid_body = solid_body - Pos(x, y, plate_thickness + frame_height/2) * Cylinder(hole_radius, hole_depth)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_frame_and_holes"
export_step(part, "output.step")