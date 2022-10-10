# MIT License
#
# Copyright (c) 2022 Quandela
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import random
import sympy as sp
import numpy
from perceval import Matrix, P, Circuit, BasicState, SVDistribution
from perceval.serialization import serialize, deserialize_matrix, deserialize_circuit, deserialize_state, \
    deserialize_svdistribution
import perceval.components.base_components as comp


def test_numeric_matrix_serialization():
    input_mat = Matrix.random_unitary(10)
    serialized_mat = serialize(input_mat)
    deserialized_mat = deserialize_matrix(serialized_mat)
    assert (input_mat == deserialized_mat).all()

    input_mat = Matrix([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]])
    serialized_mat = serialize(input_mat)
    deserialized_mat = deserialize_matrix(serialized_mat)
    assert (input_mat == deserialized_mat).all()


def test_symbolic_matrix_serialization():
    theta = P('theta')
    bs = comp.BS(theta=theta)
    input_mat = bs.U
    serialized_mat = serialize(input_mat)
    deserialized_mat = deserialize_matrix(serialized_mat)

    # Now, assign any value to theta:
    theta_value = random.random()
    theta.set_value(theta_value)
    input_mat_num = bs.compute_unitary()
    convert_to_numpy = sp.lambdify((), deserialized_mat.subs({'theta': theta_value}), modules=numpy)
    deserialized_mat_num = Matrix(convert_to_numpy())
    assert numpy.allclose(input_mat_num, deserialized_mat_num)


def _check_circuits_eq(c_a, c_b):
    assert c_a.ncomponents() == c_b.ncomponents()
    for nc in range(len(c_a._components)):
        input_idx, input_comp = c_a._components[nc]
        output_idx, output_comp = c_b._components[nc]
        assert isinstance(input_comp, type(output_comp))
        assert list(input_idx) == list(output_idx)
        assert (input_comp.compute_unitary() == output_comp.compute_unitary()).all()


def _build_test_circuit():
    c1 = Circuit(3) // comp.BS(theta=1.814) // comp.PS(phi=0.215) // comp.PERM([2, 0, 1]) // (1, comp.PBS()) \
         // comp.Unitary(Matrix.random_unitary(3))
    c2 = Circuit(2) // comp.BS.H(theta=0.36, phi_tl=1.94, phi_br=5.8817, phi_bl=0.0179) // comp.PERM([1, 0])
    c1.add(1, c2, merge=False).add(0, comp.HWP(xsi=0.23)).add(1, comp.QWP(xsi=0.17)).add(2, comp.WP(0.4, 0.5))
    c1.add(0, comp.PR(delta=0.89))
    return c1


def test_circuit_serialization():
    c1 = _build_test_circuit()
    serialized_c1 = serialize(c1)
    deserialized_c1 = deserialize_circuit(serialized_c1)
    _check_circuits_eq(c1, deserialized_c1)


def test_fockstate_serialization():
    states = [
        BasicState("|0,1>"),
        BasicState([0, 1, 0, 0, 1, 0]),
        BasicState("|{P:H}{P:V},0>")
    ]
    for s in states:
        serialized = serialize(s)
        deserialized = deserialize_state(serialized)
        assert s == deserialized


def test_svdistribution_deserialization():
    svd = SVDistribution()
    svd[BasicState("|0,1>")] = 0.2
    svd[BasicState("|1,0>")] = 0.3
    svd[BasicState("|1,1>")] = 0.5
    json = '{"|0,1>":0.2,"|1,0>":0.3,"|1,1>":0.5}'
    svd2 = deserialize_svdistribution(json)
    assert svd == svd2
