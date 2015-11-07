# Copyright 2014, 2015 The ODL development group
#
# This file is part of ODL.
#
# ODL is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ODL is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ODL.  If not, see <http://www.gnu.org/licenses/>.


# Imports for common Python 2/3 codebase
from __future__ import print_function, division, absolute_import

from future import standard_library
standard_library.install_aliases()


# External module imports
import pytest
import numpy as np

import odl

from odl.util.testutils import all_equal, skip_if_no_cuda


def test_init():
    # Validate that the different init patterns work and do not crash.
    space = odl.FunctionSpace(odl.Interval(0, 1))
    grid = odl.uniform_sampling(space.domain, 10)
    R10 = odl.Rn(10)
    odl.DiscreteL2(space, grid, R10)

    # Normal discretization of unit interval with complex
    complex_space = odl.FunctionSpace(odl.Interval(0, 1),
                                      field=odl.ComplexNumbers())
    C10 = odl.Cn(10)
    odl.DiscreteL2(complex_space, grid, C10)

    # Real space should not work with complex
    with pytest.raises(ValueError):
        odl.DiscreteL2(space, grid, C10)

    # Complex space should not work with reals
    with pytest.raises(ValueError):
        odl.DiscreteL2(complex_space, grid, R10)

    # Wrong size of underlying space
    R20 = odl.Rn(20)
    with pytest.raises(ValueError):
        odl.DiscreteL2(space, grid, R20)


@skip_if_no_cuda
def test_init_cuda():
    # Normal discretization of unit interval
    space = odl.FunctionSpace(odl.Interval(0, 1))
    grid = odl.uniform_sampling(space.domain, 10)
    R10 = odl.CudaRn(10)
    odl.DiscreteL2(space, grid, R10)


def test_factory():
    space = odl.FunctionSpace(odl.Interval(0, 1))
    discr = odl.l2_uniform_discr(space, 10, impl='numpy')

    assert isinstance(discr.dspace, odl.Rn)

    # Complex
    space = odl.FunctionSpace(odl.Interval(0, 1), field=odl.ComplexNumbers())
    discr = odl.l2_uniform_discr(space, 10, impl='numpy')

    assert isinstance(discr.dspace, odl.Cn)


@skip_if_no_cuda
def test_factory_cuda():
    space = odl.FunctionSpace(odl.Interval(0, 1))
    discr = odl.l2_uniform_discr(space, 10, impl='cuda')
    assert isinstance(discr.dspace, odl.CudaRn)

    # Cuda currently does not support complex numbers, check error
    space = odl.FunctionSpace(odl.Interval(0, 1), field=odl.ComplexNumbers())
    with pytest.raises(NotImplementedError):
        odl.l2_uniform_discr(space, 10, impl='cuda')


def test_factory_dtypes():
    space = odl.FunctionSpace(odl.Interval(0, 1))

    # valid types
    for dtype in [np.int8, np.int16, np.int32, np.int64,
                  np.uint8, np.uint16, np.uint32, np.uint64,
                  np.float32, np.float64]:
        discr = odl.l2_uniform_discr(space, 10, impl='numpy', dtype=dtype)
        assert isinstance(discr.dspace, odl.Fn)
        assert discr.dspace.element().space.dtype == dtype

    # invalid types
    for dtype in [np.complex64, np.complex128]:
        with pytest.raises(TypeError):
            odl.l2_uniform_discr(space, 10, impl='numpy', dtype=dtype)


@skip_if_no_cuda
def test_factory_dtypes_cuda():
    space = odl.FunctionSpace(odl.Interval(0, 1))

    # valid types
    for dtype in odl.space.cu_ntuples.CUDA_DTYPES:
        discr = odl.l2_uniform_discr(space, 10, impl='cuda', dtype=dtype)
        assert isinstance(discr.dspace, odl.CudaFn)
        assert discr.dspace.element().space.dtype == dtype


def test_factory_nd():
    # 2d
    square_space = odl.FunctionSpace(odl.Rectangle([0, 0], [1, 1]))
    odl.l2_uniform_discr(square_space, (5, 5))

    # 3d
    cube_space = odl.FunctionSpace(odl.Cuboid([0, 0, 0], [1, 1, 1]))
    odl.l2_uniform_discr(cube_space, (5, 5, 5))

    # nd
    cube10_space = odl.FunctionSpace(odl.IntervalProd([0]*10, [1]*10))
    odl.l2_uniform_discr(cube10_space, (5,)*10)


def test_element_1d():
    space = odl.FunctionSpace(odl.Interval(0, 1))
    discr = odl.l2_uniform_discr(space, 3, impl='numpy')
    vec = discr.element()
    assert isinstance(vec, discr.Vector)
    assert isinstance(vec.ntuple, odl.Rn.Vector)


def test_element_2d():
    space = odl.FunctionSpace(odl.Rectangle([0, 0], [1, 1]))
    discr = odl.l2_uniform_discr(space, (3, 3), impl='numpy')
    vec = discr.element()
    assert isinstance(vec, discr.Vector)
    assert isinstance(vec.ntuple, odl.Rn.Vector)


def test_element_from_array_1d():
    space = odl.FunctionSpace(odl.Interval(0, 1))
    discr = odl.l2_uniform_discr(space, 3, impl='numpy')
    vec = discr.element([1, 2, 3])

    assert isinstance(vec, discr.Vector)
    assert isinstance(vec.ntuple, odl.Rn.Vector)
    assert all_equal(vec.ntuple, [1, 2, 3])


def test_element_from_array_2d():
    # assert orderings work properly with 2d
    square_space = odl.FunctionSpace(odl.Rectangle([0, 0], [1, 1]))
    discr = odl.l2_uniform_discr(square_space, (2, 2), impl='numpy',
                                 order='C')
    vec = discr.element([[1, 2],
                         [3, 4]])

    assert isinstance(vec, discr.Vector)
    assert isinstance(vec.ntuple, odl.Rn.Vector)

    # Check ordering
    assert all_equal(vec.ntuple, [1, 2, 3, 4])

    # Linear creation works aswell
    linear_vec = discr.element([1, 2, 3, 4])
    assert all_equal(vec.ntuple, [1, 2, 3, 4])

    # Fortran order
    discr = odl.l2_uniform_discr(square_space, (2, 2), impl='numpy', order='F')
    vec = discr.element([[1, 2],
                         [3, 4]])

    # Check ordering
    assert all_equal(vec.ntuple, [1, 3, 2, 4])

    # Linear creation works aswell
    linear_vec = discr.element([1, 2, 3, 4])
    assert all_equal(linear_vec.ntuple, [1, 2, 3, 4])


def test_element_from_array_2d_shape():
    # Verify that the shape is correctly tested for
    square_space = odl.FunctionSpace(odl.Rectangle([0, 0], [1, 1]))
    discr = odl.l2_uniform_discr(square_space, (3, 2), impl='numpy', order='C')

    # Correct order
    discr.element([[1, 2],
                   [3, 4],
                   [5, 6]])

    # Wrong order, should throw
    with pytest.raises(ValueError):
        discr.element([[1, 2, 3],
                       [4, 5, 6]])

    # Wrong number of elements, should throw
    with pytest.raises(ValueError):
        discr.element([[1, 2],
                       [3, 4]])


def test_zero():
    discr = odl.l2_uniform_discr(odl.FunctionSpace(odl.Interval(0, 1)), 3)
    vec = discr.zero()

    assert isinstance(vec, discr.Vector)
    assert isinstance(vec.ntuple, odl.Rn.Vector)
    assert all_equal(vec, [0, 0, 0])


def test_getitem():
    discr = odl.l2_uniform_discr(odl.FunctionSpace(odl.Interval(0, 1)), 3)
    vec = discr.element([1, 2, 3])

    assert all_equal(vec, [1, 2, 3])


def test_getslice():
    discr = odl.l2_uniform_discr(odl.FunctionSpace(odl.Interval(0, 1)), 3)
    vec = discr.element([1, 2, 3])

    assert isinstance(vec[:], odl.Rn.Vector)
    assert all_equal(vec[:], [1, 2, 3])

    discr = odl.l2_uniform_discr(
        odl.FunctionSpace(odl.Interval(0, 1), field=odl.ComplexNumbers()),
        3)
    vec = discr.element([1+2j, 2-2j, 3])

    assert isinstance(vec[:], odl.Cn.Vector)
    assert all_equal(vec[:], [1+2j, 2-2j, 3])


def test_setitem():
    discr = odl.l2_uniform_discr(odl.FunctionSpace(odl.Interval(0, 1)), 3)
    vec = discr.element([1, 2, 3])
    vec[0] = 4
    vec[1] = 5
    vec[2] = 6

    assert all_equal(vec, [4, 5, 6])


def test_setitem_nd():

    # 1D
    discr = odl.l2_uniform_discr(odl.FunctionSpace(odl.Interval(0, 1)), 3)
    vec = discr.element([1, 2, 3])

    vec[:] = [4, 5, 6]
    assert all_equal(vec, [4, 5, 6])

    vec[:] = np.array([3, 2, 1])
    assert all_equal(vec, [3, 2, 1])

    vec[:] = 0
    assert all_equal(vec, [0, 0, 0])

    vec[:] = [1]
    assert all_equal(vec, [1, 1, 1])

    with pytest.raises(ValueError):
        vec[:] = [0, 0]  # bad shape

    with pytest.raises(ValueError):
        vec[:] = [0, 0, 1, 2]  # bad shape

    # 2D
    discr = odl.l2_uniform_discr(
        odl.FunctionSpace(odl.Rectangle([0, 0], [1, 1])), [3, 2])

    vec = discr.element([[1, 2],
                         [3, 4],
                         [5, 6]])

    vec[:] = [[-1, -2],
              [-3, -4],
              [-5, -6]]
    assert all_equal(vec, [-1, -2, -3, -4, -5, -6])

    arr = np.arange(6, 12).reshape([3, 2])
    vec[:] = arr
    assert all_equal(vec, np.arange(6, 12))

    vec[:] = 0
    assert all_equal(vec, [0]*6)

    vec[:] = [1]
    assert all_equal(vec, [1]*6)

    with pytest.raises(ValueError):
        vec[:] = [0, 0]  # bad shape

    with pytest.raises(ValueError):
        vec[:] = [0, 0, 0]  # bad shape

    with pytest.raises(ValueError):
        vec[:] = np.arange(6)[:, np.newaxis]  # bad shape (6, 1)

    with pytest.raises(ValueError):
        arr = np.arange(6, 12).reshape([3, 2])
        vec[:] = arr.T  # bad shape (2, 3)

    # nD
    cube10_space = odl.FunctionSpace(odl.IntervalProd([0]*6, [1]*6))
    shape = (3,)*3 + (4,)*3
    discr = odl.l2_uniform_discr(cube10_space, shape)
    ntotal = np.prod(shape)
    vec = discr.element(np.zeros(shape))

    arr = np.arange(ntotal).reshape(shape)

    vec[:] = arr
    assert all_equal(vec, np.arange(ntotal))

    vec[:] = 0
    assert all_equal(vec, np.zeros(ntotal))

    vec[:] = [1]
    assert all_equal(vec, np.ones(ntotal))

    with pytest.raises(ValueError):
        # Reversed shape -> bad
        vec[:] = np.arange(ntotal).reshape((4,)*3 + (3,)*3)


def test_setslice():
    discr = odl.l2_uniform_discr(odl.FunctionSpace(odl.Interval(0, 1)), 3)
    vec = discr.element([1, 2, 3])

    vec[:] = [4, 5, 6]
    assert all_equal(vec, [4, 5, 6])


def test_asarray_2d():
    square_space = odl.FunctionSpace(odl.Rectangle([0, 0], [1, 1]))
    discr_F = odl.l2_uniform_discr(square_space, (2, 2), order='F')
    vec_F = discr_F.element([[1, 2],
                             [3, 4]])

    # Verify that returned array equals input data
    assert all_equal(vec_F.asarray(), [[1, 2],
                                       [3, 4]])
    # Check order of out array
    assert vec_F.asarray().flags['F_CONTIGUOUS']

    # Also check with C ordering
    discr_C = odl.l2_uniform_discr(square_space, (2, 2), order='C')
    vec_C = discr_C.element([[1, 2],
                             [3, 4]])

    # Verify that returned array equals input data
    assert all_equal(vec_C.asarray(), [[1, 2],
                                       [3, 4]])

    # Check order of out array
    assert vec_C.asarray().flags['C_CONTIGUOUS']


def test_transpose():
    square_space = odl.FunctionSpace(odl.Rectangle([0, 0], [1, 1]))
    discr = odl.l2_uniform_discr(square_space, (2, 2), order='F')
    x = discr.element([[1, 2], [3, 4]])
    y = discr.element([[5, 6], [7, 8]])

    assert isinstance(x.T, odl.Operator)
    assert x.T.is_linear

    assert x.T(y) == x.inner(y)
    assert x.T.T == x
    assert all_equal(x.T.adjoint(1.0), x)

if __name__ == '__main__':
    pytest.main(str(__file__.replace('\\', '/')) + ' -v')
