import pcbnew
import json
import wx
import math


CENTER_X = 150
CENTER_Y = 100


def create_tracks(board, group, net, layer, thickness, coords):
    last_x = None
    last_y = None
    for coord in coords:
        x = coord["x"] + CENTER_X
        y = coord["y"] + CENTER_Y
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
        self.name = "Create coil"
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
                pin_diameter = coil_data["parameters"]["pinDiameter"]
                pin_drill = coil_data["parameters"]["pinDrillDiameter"]
                via_diameter = coil_data["parameters"]["viaDiameter"]
                via_drill_diameter = coil_data["parameters"]["viaDrillDiameter"]

                # put everything in a group to make it easier to manage
                pcb_group = pcbnew.PCB_GROUP(board)
                # board.Add(pcb_group)
                # find the matching net for the track
                net = board.FindNet("coils")
                if net is None:
                    net = pcbnew.NETINFO_ITEM(board, "coils")
                    board.Add(net)
                    # raise "Net not found: {}".format(track["net"])

                # create tracks
                for track in coil_data["tracks"]["f"]:
                    create_tracks(
                        board, pcb_group, net, pcbnew.F_Cu, track_width, track
                    )

                for track in coil_data["tracks"]["b"]:
                    create_tracks(
                        board, pcb_group, net, pcbnew.B_Cu, track_width, track
                    )

                for track in coil_data["tracks"]["in1"]:
                    create_tracks(
                        board, pcb_group, net, pcbnew.In1_Cu, track_width, track
                    )

                for track in coil_data["tracks"]["in2"]:
                    create_tracks(
                        board, pcb_group, net, pcbnew.In2_Cu, track_width, track
                    )


                # create the vias
                for via in coil_data["vias"]:
                    pcb_via = pcbnew.PCB_VIA(board)
                    pcb_via.SetPosition(
                        pcbnew.wxPointMM(via["x"] + CENTER_X, via["y"] + CENTER_Y)
                    )
                    pcb_via.SetWidth(int(via_diameter * 1e6))
                    pcb_via.SetDrill(int(via_drill_diameter * 1e6))
                    pcb_via.SetNetCode(net.GetNetCode())
                    board.Add(pcb_via)
                    # pcb_group.AddItem(pcb_via)

                # create the pins
                # for pin in coil_data["pins"]:
                #     x = pin["x"] + CENTER_X
                #     y = pin["y"] + CENTER_Y
                #     module = pcbnew.FOOTPRINT(board)
                #     module.SetPosition(pcbnew.wxPointMM(x, y))
                #     board.Add(module)
                #     pcb_pad = pcbnew.PAD(module)
                #     pcb_pad.SetSize(pcbnew.wxSizeMM(pin_diameter, pin_diameter))
                #     pcb_pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
                #     pcb_pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
                #     pcb_pad.SetLayerSet(pcb_pad.PTHMask())
                #     pcb_pad.SetDrillSize(pcbnew.wxSizeMM(pin_drill, pin_drill))
                #     pcb_pad.SetPosition(pcbnew.wxPointMM(x, y))
                #     pcb_pad.SetNetCode(net.GetNetCode())
                #     module.Add(pcb_pad)

                # create the pads
                lset = pcbnew.LSET()
                lset.AddLayer(pcbnew.B_Cu)
                for pin in coil_data["pads"]:
                    x = pin["x"] + CENTER_X
                    y = pin["y"] + CENTER_Y
                    module = pcbnew.FOOTPRINT(board)
                    module.SetPosition(pcbnew.wxPointMM(x, y))
                    board.Add(module)
                    pcb_pad = pcbnew.PAD(module)
                    pcb_pad.SetSize(pcbnew.wxSizeMM(pin["width"], pin["height"]))
                    pcb_pad.SetShape(pcbnew.PAD_SHAPE_RECT)
                    pcb_pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
                    pcb_pad.SetLayerSet(pcb_pad.SMDMask())
                    # pcb_pad.SetLayerSet(lset)
                    pcb_pad.SetPosition(pcbnew.wxPointMM(x, y))
                    pcb_pad.SetNetCode(net.GetNetCode())
                    pcb_pad.Flip(pcbnew.wxPointMM(x, y), False)
                    module.Add(pcb_pad)

                # create any silk screen
                for text in coil_data["silk"]:
                    x = text["x"] + CENTER_X
                    y = text["y"] + CENTER_Y
                    pcb_txt = pcbnew.PCB_TEXT(board)
                    pcb_txt.SetText(text["text"])
                    pcb_txt.SetPosition(pcbnew.wxPointMM(x, y))
                    pcb_txt.SetHorizJustify(pcbnew.GR_TEXT_HJUSTIFY_CENTER)
                    pcb_txt.Rotate(pcbnew.wxPointMM(x, y), text["angle"])
                    pcb_txt.SetTextSize(
                        pcbnew.wxSize(
                            text["size"] * pcbnew.IU_PER_MM,
                            text["size"] * pcbnew.IU_PER_MM,
                        )
                    )
                    pcb_txt.SetLayer(pcbnew.F_SilkS)
                    if text["layer"] == "b":
                        pcb_txt.Flip(pcbnew.wxPointMM(x, y), True)
                    board.Add(pcb_txt)
                    # pcb_group.AddItem(pcb_txt)

                # create the mounting holes
                # for hole in coil_data["mountingHoles"]:
                #     x = hole["x"] + CENTER_X
                #     y = hole["y"] + CENTER_Y
                #     module = pcbnew.FOOTPRINT(board)
                #     module.SetPosition(pcbnew.wxPointMM(x, y))
                #     board.Add(module)
                #     pcb_pad = pcbnew.PAD(module)
                #     pcb_pad.SetSize(pcbnew.wxSizeMM(hole["diameter"], hole["diameter"]))
                #     pcb_pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
                #     pcb_pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
                #     # pcb_pad.SetLayerSet(pcb_pad.NPTHMask())
                #     pcb_pad.SetDrillSize(
                #         pcbnew.wxSizeMM(hole["diameter"], hole["diameter"])
                #     )
                #     pcb_pad.SetPosition(pcbnew.wxPointMM(x, y))
                #     module.Add(pcb_pad)
                    # pcb_group.AddItem(pcb_hole)

                # crate the edge cuts
                for edge_cut in coil_data["edgeCuts"]:
                    ec = pcbnew.PCB_SHAPE(board)
                    ec.SetShape(pcbnew.SHAPE_T_POLY)
                    ec.SetFilled(False)
                    ec.SetLayer(pcbnew.Edge_Cuts)
                    ec.SetWidth(int(0.1 * pcbnew.IU_PER_MM))
                    v = pcbnew.wxPoint_Vector()
                    for point in edge_cut:
                        x = point["x"] + CENTER_X
                        y = point["y"] + CENTER_Y
                        v.append(pcbnew.wxPointMM(x, y))
                    ec.SetPolyPoints(v)
                    board.Add(ec)


CoilPlugin().register()  # Instantiate and register to Pcbnew])
