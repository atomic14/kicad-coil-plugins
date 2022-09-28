import pcbnew
import numpy as np

VIA_DIAM = 0.8
VIA_DRILL = 0.4
TRACK_THICKNESS = 0.2
TRACK_SPACING = 0.2
SEGMENT_LENGTH = 2 * 2*np.pi/360.0
STATOR_RADIUS = 20
STATOR_HOLE_RADIUS = 4
INNER_RADIUS = 1
# each coil is in the middle of the stator radius
OUTER_RADIUS = (0.5 * STATOR_RADIUS * np.pi) / 6 - TRACK_SPACING


def spiral(angle, distance, inner_radius, outer_radius, track_width, track_spacing, direction=1):
    thickness = track_width + track_spacing
    number_turns = (outer_radius - inner_radius)//thickness
    # create a starting point in the center
    yield distance * np.cos(angle), distance * np.sin(angle)
    for theta in np.arange(0, number_turns * 2*np.pi, 0.1):
        radius = inner_radius + thickness * theta/(2*np.pi)
        if direction == -1:
            x = radius*np.cos(direction * (theta + np.pi))
            y = radius*np.sin(direction * (theta + np.pi))
        else:
            x = radius*np.cos(direction * (theta))
            y = radius*np.sin(direction * (theta))
        # rotate by angle
        x, y = x*np.cos(angle) - y*np.sin(angle), x*np.sin(angle) + y*np.cos(angle)
        # translate by distance
        x, y = x + distance * np.cos(angle), y + distance * np.sin(angle)
        yield x, y


def create_tracks(board, group, coords, layer):
    last_x = None
    last_y = None
    for x, y in coords:
        track = pcbnew.PCB_TRACK(board)
        if last_x is not None:
            track.SetStart(pcbnew.wxPointMM(float(last_x), float(last_y)))
            track.SetEnd(pcbnew.wxPointMM(float(x), float(y)))
            track.SetWidth(int(TRACK_THICKNESS * 1e6))
            track.SetLayer(layer)
            board.Add(track)
            group.AddItem(track)
        last_x = x
        last_y = y


class CoilPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Create coil 2"
        self.category = "Coils"
        self.description = "Creates a coil"
        # self.show_toolbar_button = False # Optional, defaults to False
        # self.icon_file_name = os.path.join(os.path.dirname(__file__), 'simple_plugin.png') # Optional, defaults to ""

    def Run(self):
        board = pcbnew.GetBoard()
        # create the center hole
        arc = pcbnew.PCB_SHAPE(board)
        arc.SetShape(pcbnew.SHAPE_T_ARC)
        arc.SetStart(pcbnew.wxPointMM(STATOR_HOLE_RADIUS, 0))
        arc.SetCenter(pcbnew.wxPointMM(0, 0))
        arc.SetArcAngleAndEnd(0, False)
        arc.SetLayer(pcbnew.Edge_Cuts)
        arc.SetWidth(int(0.1 * pcbnew.IU_PER_MM))
        board.Add(arc)
        # create six coils equally spaced around the origin
        for angle in np.arange(0, 2*np.pi, 2*np.pi/6):
            group = pcbnew.PCB_GROUP(board)
            board.Add(group)

            coords = spiral(angle, STATOR_RADIUS/2, INNER_RADIUS, OUTER_RADIUS, TRACK_THICKNESS, TRACK_SPACING, 1)
            create_tracks(board, group, coords, pcbnew.F_Cu)
            coords = spiral(angle, STATOR_RADIUS/2, INNER_RADIUS, OUTER_RADIUS, TRACK_THICKNESS, TRACK_SPACING, -1)
            create_tracks(board, group, coords, pcbnew.B_Cu)
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.wxPointMM(float(STATOR_RADIUS/2 * np.cos(angle)), float(STATOR_RADIUS/2 * np.sin(angle))))
            via.SetWidth(int(VIA_DIAM * 1e6))
            via.SetDrill(int(VIA_DRILL * 1e6))
            board.Add(via)
            group.AddItem(via)


CoilPlugin().register()  # Instantiate and register to Pcbnew
