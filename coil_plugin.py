import pcbnew
import json
import wx


def create_tracks(board, group, net, layer, thickness, coords):
    last_x = None
    last_y = None
    for coord in coords:
        x = coord["x"]
        y = coord["y"]
        track = pcbnew.PCB_TRACK(board)
        if last_x is not None:
            track.SetStart(pcbnew.wxPointMM(float(last_x), float(last_y)))
            track.SetEnd(pcbnew.wxPointMM(float(x), float(y)))
            track.SetWidth(int(thickness * 1e6))
            track.SetLayer(layer)
            if net is not None:
                track.SetNetCode(net.GetNetCode())
            board.Add(track)
            # group.AddItem(track)
        last_x = x
        last_y = y


class CoilPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Create coil 3"
        self.category = "Coils"
        self.description = "Creates a coil"
        # self.show_toolbar_button = False # Optional, defaults to False
        # self.icon_file_name = os.path.join(os.path.dirname(__file__), 'simple_plugin.png') # Optional, defaults to ""

    def Run(self):
        # launch a file picker dialog to get the coil file
        dialog = wx.FileDialog(None, "Choose a coil file", "", "", "*.json", wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            # read the file
            with open(dialog.GetPath(), "r") as f:
                board = pcbnew.GetBoard()
                # load up the JSON with the coil parameters
                coil_data = json.load(f)
                # parameters
                track_width = coil_data["parameters"]["trackWidth"]
                stator_hole_radius = coil_data["parameters"]["statorHoleRadius"]
                stator_radius = coil_data["parameters"]["statorRadius"]
                via_diameter = coil_data["parameters"]["viaDiameter"]
                via_drill_diameter = coil_data["parameters"]["viaDrillDiameter"]

                # put everything in a group to make it easier to manage
                pcb_group = pcbnew.PCB_GROUP(board)
                # board.Add(pcb_group)

                # create tracks
                for track in coil_data["tracks"]["f"]:
                    # find the matching net for the track
                    net = board.FindNet("coils")
                    if net is None:
                        net = pcbnew.NETINFO_ITEM(board, "coils")
                        board.Add(net)
                        # raise "Net not found: {}".format(track["net"])
                    create_tracks(
                        board, pcb_group, net, pcbnew.F_Cu, track_width, track
                    )

                for track in coil_data["tracks"]["b"]:
                    create_tracks(
                        board, pcb_group, net, pcbnew.B_Cu, track_width, track
                    )

                # create the vias
                for via in coil_data["vias"]:
                    pcb_via = pcbnew.PCB_VIA(board)
                    pcb_via.SetPosition(
                        pcbnew.wxPointMM(float(via["x"]), float(via["y"]))
                    )
                    pcb_via.SetWidth(int(via_diameter * 1e6))
                    pcb_via.SetDrill(int(via_drill_diameter * 1e6))
                    pcb_via.SetNetCode(net.GetNetCode())
                    board.Add(pcb_via)
                    # pcb_group.AddItem(pcb_via)

                # create the pads
                for pad in coil_data["pads"]:
                    module = pcbnew.FOOTPRINT(board)
                    module.SetPosition(pcbnew.wxPointMM(pad["x"], pad["y"]))
                    board.Add(module)
                    pcb_pad = pcbnew.PAD(module)
                    pcb_pad.SetSize(pcbnew.wxSizeMM(1.7, 1.7))
                    pcb_pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
                    pcb_pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
                    pcb_pad.SetLayerSet(pcb_pad.PTHMask())
                    pcb_pad.SetDrillSize(pcbnew.wxSizeMM(1.0, 1.0))
                    pcb_pad.SetPosition(pcbnew.wxPointMM(pad["x"], pad["y"]))
                    pcb_pad.SetNetCode(net.GetNetCode())
                    module.Add(pcb_pad)

                # create any silk screen
                for text in coil_data["silk"]:
                    pcb_txt = pcbnew.PCB_TEXT(board)
                    pcb_txt.SetText(text["text"])
                    pcb_txt.SetPosition(pcbnew.wxPointMM(text["x"], text["y"]))
                    pcb_txt.SetHorizJustify(pcbnew.GR_TEXT_HJUSTIFY_CENTER)
                    pcb_txt.SetTextSize(pcbnew.wxSize(5000000, 5000000))
                    pcb_txt.SetLayer(pcbnew.F_SilkS)
                    board.Add(pcb_txt)
                    # pcb_group.AddItem(pcb_txt)


                # create the stator outline
                arc = pcbnew.PCB_SHAPE(board)
                arc.SetShape(pcbnew.SHAPE_T_CIRCLE)
                arc.SetFilled(False)
                arc.SetStart(pcbnew.wxPointMM(0, 0))
                arc.SetEnd(pcbnew.wxPointMM(stator_radius, 0))
                arc.SetCenter(pcbnew.wxPointMM(0, 0))                
                arc.SetLayer(pcbnew.Edge_Cuts)
                arc.SetWidth(int(0.1 * pcbnew.IU_PER_MM))
                board.Add(arc)
                # pcb_group.AddItem(arc)

                # create the center hole
                arc = pcbnew.PCB_SHAPE(board)
                arc.SetShape(pcbnew.SHAPE_T_CIRCLE)
                arc.SetFilled(False)
                arc.SetStart(pcbnew.wxPointMM(0, 0))
                arc.SetEnd(pcbnew.wxPointMM(stator_hole_radius, 0))
                arc.SetCenter(pcbnew.wxPointMM(0, 0))
                arc.SetLayer(pcbnew.Edge_Cuts)
                arc.SetWidth(int(0.1 * pcbnew.IU_PER_MM))
                board.Add(arc)
                # pcb_group.AddItem(arc)

CoilPlugin().register()  # Instantiate and register to Pcbnew])
