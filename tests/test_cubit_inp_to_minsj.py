"""This module is a unit test for .inp file input to minimum
scaled Jacobian .csv file output via Cubit translation.

To run:
(atmeshenv) ~/autotwin/mesh> pytest tests/test_cubit_inp_to_minsj.py -v
(atmeshenv) ~/autotwin/mesh> pytest tests/test_cubit_inp_to_minsj.py -vs  # --capture=no

For coverage:
(atmeshenv) ~/autotwin/mesh> pytest tests/test_cubit_inp_to_minsj.py --cov=src/atmesh --cov-report term-missing
"""


# import os
from pathlib import Path

import atmesh.cubit_inp_to_minsj as translator


def test_known_element_count():
    self_path_file = Path(__file__)
    self_path = self_path_file.resolve().parent
    data_path = self_path.joinpath("files").resolve()
    input_path_file = data_path.joinpath("sphere_minsj.yml")
    found = translator.translate(path_file_input=str(input_path_file))
    known = 352  # number of hex elements

    assert known == found
