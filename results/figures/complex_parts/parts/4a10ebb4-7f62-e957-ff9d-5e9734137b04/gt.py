from build123d import *

base = Box(80, 50, 30)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-2, openings=[bottom_face])

bottom_plate = Pos(0, 0, -17) * Box(76, 46, 4)
base = base + bottom_plate

wall = Pos(0, 0, -21.5) * Box(76, 2, 5)
base = base + wall

part = base
part.name = "shelled_box_with_bottom_plate_and_wall"
export_step(part, OUTPUT_PATH)