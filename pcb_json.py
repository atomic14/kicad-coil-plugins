import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from helpers import rotate


def create_pin(radius, angle, name, net_name):
    return {
        "x": radius * np.cos(np.deg2rad(angle)),
        "y": radius * np.sin(np.deg2rad(angle)),
        "name": name,
        "net": net_name,
    }


def create_pad(point, width, height, layer, net_name, angle=0):
    return {
        "x": point[0],
        "y": point[1],
        "width": width,
        "height": height,
        "layer": layer,
        "angle": angle,
        "net": net_name,
    }


def create_silk(point, text, layer="f", size=1, angle=0):
    return {
        "x": point[0],
        "y": point[1],
        "text": text,
        "layer": layer,
        "size": size,
        "angle": angle,
    }


def create_via(point, net_name):
    return {"x": point[0], "y": point[1], "net": net_name}


# def create_track(points, net_name):
#     return [{"x": x, "y": y, "net": net_name} for x, y in points]


def create_mounting_hole(point, diameter):
    return {
        "x": point[0],
        "y": point[1],
        "diameter": diameter,
    }


def create_track_json(points):
    return [{"x": x, "y": y} for x, y in points]


def dump_json(
    filename,
    track_width,
    pin_diam,
    pin_drill,
    via_diam,
    via_drill,
    vias,
    pins,
    pads,
    silk,
    tracks_f,
    tracks_in,
    tracks_b,
    mounting_holes,
    edge_cuts,
    components
):
    tracks_inner = [[
        {
            "net":track_info["net"], 
            "width": track_info["width"] if "width" in track_info else track_width,
            "pts":create_track_json(track_info["pts"]),
        } 
        for track_info in track_vals]
        for i, track_vals in enumerate(tracks_in)]

    tracks = {
        "b": [
            {
                "net":track_info["net"],
                "width": track_info["width"] if "width" in track_info else track_width,
                "pts":create_track_json(track_info["pts"]),
            }
            for track_info in tracks_b],

        "f": [
            {
                "net":track_info["net"],
                "width": track_info["width"] if "width" in track_info else track_width,
                "pts":create_track_json(track_info["pts"]),
            }
            for track_info in tracks_f],

        "in": tracks_inner
    }

    # dump out the results to json
    json_result = {
        "parameters": {
            "trackWidth": track_width,
            "viaDiameter": via_diam,
            "viaDrillDiameter": via_drill,
            "pinDiameter": pin_diam,
            "pinDrillDiameter": pin_drill,
        },
        "vias": vias,
        "pins": pins,
        "pads": pads,
        "silk": silk,
        "tracks": tracks,
        "mountingHoles": mounting_holes,
        "edgeCuts": [create_track_json(points) for points in edge_cuts],
        "components": components,
    }
    json.dump(json_result, open(filename, "w"))
    return json_result


def plot_json(json_result):
    pin_diam = json_result["parameters"]["pinDiameter"]
    pin_drill = json_result["parameters"]["pinDrillDiameter"]
    # track_width = json_result["parameters"]["trackWidth"]
    via_dim = json_result["parameters"]["viaDiameter"]
    via_drill = json_result["parameters"]["viaDrillDiameter"]
    # plot the back tracks
    ax = None
    for track in json_result["tracks"]["b"]:
        df = pd.DataFrame(track["pts"], columns=["x", "y"])
        ax = df.plot.line(x="x", y="y", color="blue", ax=ax)
        ax.axis("equal")

    colors = ["green", "orange", "cyan", "magenta"]
    color_index = 0
    # plot the inner tracks
    for index in json_result["tracks"]["in"]:
        for track in index:
            df = pd.DataFrame(track["pts"], columns=["x", "y"])
            ax = df.plot.line(x="x", y="y", color=colors[color_index % 4], ax=ax)
            ax.axis("equal")
        color_index += 1

    # plot the front tracks
    for track in json_result["tracks"]["f"]:
        df = pd.DataFrame(track["pts"], columns=["x", "y"])
        ax = df.plot.line(x="x", y="y", color="red", ax=ax)
        ax.axis("equal")

    # set the axis range
    ax.set_xlim(-30, 30)
    ax.set_ylim(-30, 30)
    ax.invert_yaxis() # match KiCAD where y-axis is inverted (numbers inrease DOWN the screen)

    # plot the pads
    for pad in json_result["pads"]:
        color = "red"
        if pad["layer"] == "b":
            color = "blue"
        ax.add_patch(
            plt.Rectangle(
                (pad["x"] - pad["width"] / 2, pad["y"] - pad["height"] / 2),
                pad["width"],
                pad["height"],
                fill=True,
                color=color,
                # rotate by the angle
                angle=pad["angle"],
            )
        )

    # plot the pins
    for pin in json_result["pins"]:
        ax.add_patch(
            plt.Circle(
                (pin["x"], pin["y"]),
                radius=pin_diam / 2,
                fill=True,
                color="orange",
            )
        )
        ax.add_patch(
            plt.Circle(
                (pin["x"], pin["y"]),
                radius=pin_drill / 2,
                fill=True,
                color="white",
            )
        )

    # plot the silk
    for silk in json_result["silk"]:
        color = "cyan"
        if silk["layer"] == "b":
            color = "magenta"
        ax.text(
            silk["x"],
            silk["y"],
            silk["text"],
            horizontalalignment="center",
            verticalalignment="center",
            color=color,
            fontsize=silk["size"] * 10,
        )

    # plot the vias
    for via in json_result["vias"]:
        ax.add_patch(
            plt.Circle(
                (via["x"], via["y"]),
                radius=via_dim / 2,
                fill=True,
                color="black",
            )
        )
        ax.add_patch(
            plt.Circle(
                (via["x"], via["y"]),
                radius=via_drill / 2,
                fill=True,
                color="white",
            )
        )

    # plot the mounting holes
    for hole in json_result["mountingHoles"]:
        ax.add_patch(
            plt.Circle(
                (hole["x"], hole["y"]),
                radius=hole["diameter"] / 2,
                fill=False,
                color="orange",
            )
        )

    # plot the edge cuts
    for edge_cut in json_result["edgeCuts"]:
        df = pd.DataFrame(edge_cut, columns=["x", "y"])
        ax = df.plot.line(x="x", y="y", color="orange", ax=ax)

    # hide the legend
    ax.legend().set_visible(False)
    # make the plot bigger
    ax.figure.set_size_inches(11, 11)

    # save to file
    ax.figure.savefig("coils.png")
