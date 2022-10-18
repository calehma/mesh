"""This module uses Cubit to convert a .stl file into a .inp file using Sculpt.

Prerequisites:
* Python 3.7.4 is required to run Cubit 16.08 and Sculpt.
* We actually use Python 3.7.9 successfully for now.

Methods:
> cd ~/autotwin/mesh/src/atmesh

* Interactive Method
# > /usr/local/bin/python3.7 sculpt_stl_to_inp.py <input_file>.yml
> python --version
  Python 3.7.9
> python sculpt_stl_to_inp.py <input_file>.yml

* Log Method
# > /usr/local/bin/python3.7 sculpt_stl_to_inp.py <input_file>.yml > sculpt_stl_to_inp.log
> python sculpt_stl_to_inp.py <input_file>.yml > sculpt_stl_to_inp.log

Example 1:
# activate the venv atmeshenv
~/autotwin/mesh> source atmeshenv/bin/activate.fish # (atmeshenv) uses Python 3.7
(atmeshenv) ~/autotwin/mesh> python src/atmesh/sculpt_stl_to_inp.py tests/files/sphere.yml

Example 2:
# uses the same venv
(atmeshenv) ~/autotwin/mesh> python src/atmesh/sculpt_stl_to_inp.py ../data/octa/octa_loop00.yml
"""

import argparse
from pathlib import Path
import sys

import atmesh.yml_to_dict as translator


def translate(*, path_file_input: str):
    # from typing import Final # Final is new in Python 3.8, Cubit uses 3.7

    # atmesh: Final[str] = "atmesh>"  # Final is new in Python 3.8, Cubit uses 3.7
    atmesh: str = "atmesh>"  # Final is new in Python 3.8, Cubit uses 3.7

    print(f"{atmesh} This is {Path(__file__).resolve()}")

    fin = Path(path_file_input).expanduser()

    if not fin.is_file():
        raise FileNotFoundError(f"{atmesh} File not found: {str(fin)}")

    # user_input = _yml_to_dict(yml_path_file=fin)
    keys = ("version", "cubit_path", "working_dir", "stl_path_file", "inp_path_file")
    user_input = translator.yml_to_dict(
        yml_path_file=fin, version=1.1, required_keys=keys
    )

    print(f"{atmesh} User input:")
    for key, value in user_input.items():
        print(f"  {key}: {value}")

    cubit_path = user_input["cubit_path"]
    inp_path_file = user_input["inp_path_file"]
    stl_path_file = user_input["stl_path_file"]
    working_dir = user_input["working_dir"]
    working_dir_str = str(Path(working_dir).expanduser())

    journaling = user_input.get("journaling", False)
    n_proc = user_input.get("n_proc", 4)  # number of parallel processors

    # bounding_box = user_input.get("bounding_box", False)  # dict | False
    bounding_box_specified = "bounding_box" in user_input
    if bounding_box_specified:
        bounding_box = user_input["bounding_box"]

    cell_count_specified = "cell_count" in user_input
    if cell_count_specified:
        cell_count = user_input["cell_count"]

    for item in [cubit_path, working_dir]:
        if not Path(item).expanduser().is_dir():
            raise OSError(f"{atmesh} Path not found: {item}")

    for item in [stl_path_file]:
        if not Path(item).expanduser().is_file():
            raise OSError(f"{atmesh} File not found: {item}")

    for item in [inp_path_file]:
        if not Path(Path(item).expanduser().parent).is_dir():
            raise OSError(f"{atmesh} Path not found: {item}")

    # append the cubit path to the system Python path
    print(f"{atmesh} Existing sys.path:")
    for item in sys.path:
        print(f"  {item}")

    sys.path.append(cubit_path)

    print(f"{atmesh} Cubit path now added:")
    for item in sys.path:
        print(f"  {item}")

    try:
        print(f"{atmesh} Import cubit module initiatied:")
        import cubit

        if journaling:
            cubit.init
            print(f"{atmesh} Import cubit module completed.  Journaling is ON.")
        else:
            cubit.init(["cubit", "-nojournal"])
            print(f"{atmesh} Import cubit module completed.  Journaling is OFF.")

        # cubit.cmd('cd "~/sibl-dev/sculpt/tests/sphere-python"')
        cc = 'cd "' + working_dir_str + '"'
        cubit.cmd(cc)
        print(f"{atmesh} The Cubit Working Directory is set to: {working_dir_str}")

        print(f"{atmesh} stl import initiatied:")
        print(f"{atmesh} Importing stl file: {stl_path_file}")
        cc = 'import stl "' + stl_path_file + '"'
        cubit.cmd(cc)
        print(f"{atmesh} stl import completed.")

        """Sculpt invocation
        Default:
        Input: /Applications/Cubit-16.06/Cubit.app/Contents/MacOS/psculpt
          --num_procs   -j  4
          --diatom_file -d  sculpt_parallel.diatom
          --exodus_file -e  sculpt_parallel.diatom_result
          --nelx        -x  26
          --nely        -y  26
          --nelz        -z  26
          --xmin        -t  -0.624136
          --ymin        -u  -0.624091
          --zmin        -v  -0.624146
          --xmax        -q  0.624042
          --ymax        -r  0.624087
          --zmax        -s  0.624033
        """

        print(f"{atmesh} Sculpt parallel initiated:")
        # cc = "sculpt parallel"
        # cc = "sculpt parallel processors 3"
        # cc = "sculpt parallel processors 2"
        # cc = "sculpt parallel processors "
        # cc = f"sculpt parallel -j {n_proc}"
        cc = f"sculpt parallel processors {n_proc}"

        if bounding_box_specified and cell_count_specified:
            nx = cell_count["nx"]
            ny = cell_count["ny"]
            nz = cell_count["nz"]

            cc += f" nelx {nx} nely {ny} nelz {nz}"

            xmin = bounding_box["xmin"]
            xmax = bounding_box["xmax"]

            ymin = bounding_box["ymin"]
            ymax = bounding_box["ymax"]

            zmin = bounding_box["zmin"]
            zmax = bounding_box["zmax"]

            cc += f" box location position {xmin} {ymin} {zmin} location position {xmax} {ymax} {zmax}"

        print(f"{atmesh} Invoking Sculpt with Cubit command: {cc}")
        cubit.cmd(cc)
        print(f"{atmesh} Sculpt parallel completed.")

        print(f"{atmesh} Abaqus file export initiated:")
        print(f"{atmesh} Exporting inp file: {inp_path_file}")
        cc = 'export abaqus "' + inp_path_file + '" overwrite'
        cubit.cmd(cc)
        print(f"{atmesh} Abaqus file export completed.")

        # print(f"{atmesh} Script: {Path(__file__).resolve()} has completed.")
        print(f"{atmesh} Done.")

    except ModuleNotFoundError as error:
        print("unable to import cubit")
        print(f"{atmesh} {error}")
        raise ModuleNotFoundError


def main():
    """Runs the module from the command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="the .yml user input file")
    args = parser.parse_args()
    input_file = args.input_file
    translate(path_file_input=input_file)


if __name__ == "__main__":
    main()
