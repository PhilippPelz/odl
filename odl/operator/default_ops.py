# Copyright 2014, 2015 Jonas Adler
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

"""Default operators defined on any (reasonable) space."""

# Imports for common Python 2/3 codebase
from __future__ import print_function, division, absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import super

# ODL imports
from odl.operator.operator import LinearOperator, SelfAdjointOperator
from odl.sets.space import LinearSpace
from odl.sets.set import CartesianProduct


__all__ = ('ScalingOperator', 'ZeroOperator', 'IdentityOperator',
           'LinCombOperator', 'MultiplyOperator')


class ScalingOperator(SelfAdjointOperator):

    """Operator of multiplication with a scalar."""

    def __init__(self, space, scalar):
        """Initialize a ScalingOperator instance.

        Parameters
        ----------
        space : `LinearSpace`
            The space of elements which the operator is acting on
        scalar : field element
            An element in the field of the space that the vectors are
            scaled with
        """
        if not isinstance(space, LinearSpace):
            raise TypeError('space {!r} not a LinearSpace instance.'
                            ''.format(space))

        self._space = space
        self._scal = float(scalar)

    def _apply(self, inp, outp):
        """Scale input and write to output.

        Parameters
        ----------
        inp : domain element
            Input vector to be scaled
        outp : range element
            Output vector to which the result is written

        Returns
        -------
        None

        Examples
        --------
        >>> from odl.space.cartesian import Rn
        >>> r3 = Rn(3)
        >>> vec = r3.element([1, 2, 3])
        >>> outp = r3.element()
        >>> op = ScalingOperator(r3, 2.0)
        >>> op(vec, outp)  # Returns outp
        Rn(3).element([2.0, 4.0, 6.0])
        >>> outp
        Rn(3).element([2.0, 4.0, 6.0])
        """
        outp.lincomb(self._scal, inp)

    def _call(self, inp):
        """Return the scaled element.

        Parameters
        ----------
        inp : domain element
            Input vector to be scaled

        Returns
        -------
        scaled : range element
            The scaled vector

        Examples
        --------
        >>> from odl.space.cartesian import Rn
        >>> r3 = Rn(3)
        >>> vec = r3.element([1, 2, 3])
        >>> op = ScalingOperator(r3, 2.0)
        >>> op(vec)
        Rn(3).element([2.0, 4.0, 6.0])
        """
        return self._scal * inp

    @property
    def inverse(self):
        """Return the inverse operator.

        Examples
        --------
        >>> from odl.space.cartesian import Rn
        >>> r3 = Rn(3)
        >>> vec = r3.element([1, 2, 3])
        >>> op = ScalingOperator(r3, 2.0)
        >>> inv = op.inverse
        >>> inv(op(vec)) == vec
        True
        >>> op(inv(vec)) == vec
        True
        """
        if self._scal == 0.0:
            raise ZeroDivisionError('scaling operator not invertible for '
                                    'scalar==0')
        return ScalingOperator(self._space, 1.0/self._scal)

    @property
    def domain(self):
        """Return the operator domain.

        Examples
        --------
        >>> from odl.space.cartesian import Rn
        >>> r3 = Rn(3)
        >>> op = ScalingOperator(r3, 2.0)
        >>> op.domain
        Rn(3)
        """
        return self._space

    @property
    def range(self):
        """Return the operator range.

        Examples
        --------
        >>> from odl.space.cartesian import Rn
        >>> r3 = Rn(3)
        >>> op = ScalingOperator(r3, 2.0)
        >>> op.range
        Rn(3)
        """
        return self._space

    def __repr__(self):
        """op.__repr__() <==> repr(op)."""
        return 'ScalingOperator({!r}, {!r})'.format(self._space, self._scal)

    def __str__(self):
        """op.__str__() <==> str(op)."""
        return '{} * I'.format(self._scal)


class ZeroOperator(ScalingOperator):

    """Operator mapping each element to the zero element."""

    def __init__(self, space):
        """Initialize a ZeroOperator instance.

        Parameters
        ----------
        space : LinearSpace
            The space of elements which the operator is acting on
        """
        super().__init__(space, 0)

    def __repr__(self):
        """op.__repr__() <==> repr(op)."""
        return 'ZeroOperator({!r})'.format(self._space)

    def __str__(self):
        """op.__str__() <==> str(op)."""
        return '0'


class IdentityOperator(ScalingOperator):

    """Operator mapping each element to itself."""

    def __init__(self, space):
        """Initialize an IdentityOperator instance.

        Parameters
        ----------
        space : LinearSpace
            The space of elements which the operator is acting on
        """
        super().__init__(space, 1)

    def __repr__(self):
        """op.__repr__() <==> repr(op)."""
        return 'IdentityOperator({!r})'.format(self._space)

    def __str__(self):
        """op.__str__() <==> str(op)."""
        return "I"


class LinCombOperator(LinearOperator):

    """Operator mapping two space elements to a linear combination.

    This opertor calculates:

    outp = a*inp[0] + b*inp[1]
    """

    # pylint: disable=abstract-method
    def __init__(self, space, a, b):
        """Initialize a LinCombOperator instance.

        Parameters
        ----------
        space : LinearSpace
            The space of elements which the operator is acting on
        a : scalar
            Scalar to multiply inp[0] with
        b : scalar
            Scalar to multiply inp[1] with
        """
        self.domain = CartesianProduct(space, space)
        self.range = space
        self.a = a
        self.b = b

    def _apply(self, inp, outp):
        """Linearly combine the input and write to output.

        Parameters
        ----------
        inp : domain element
            An element in the operator domain (2-tuple of space
            elements) whose linear combination is calculated
        outp : range element
            Vector to which the result is written

        Examples
        --------
        >>> from odl.space.cartesian import Rn
        >>> r3 = Rn(3)
        >>> x = r3.element([1, 2, 3])
        >>> y = r3.element([1, 2, 3])
        >>> z = r3.element()
        >>> op = LinCombOperator(r3, 1.0, 1.0)
        >>> op([x, y], z)  # Returns z
        Rn(3).element([2.0, 4.0, 6.0])
        >>> z
        Rn(3).element([2.0, 4.0, 6.0])
        """
        outp.lincomb(self.a, inp[0], self.b, inp[1])

    def __repr__(self):
        """op.__repr__() <==> repr(op)."""
        return 'LinCombOperator({!r}, {!r}, {!r})'.format(
            self.range, self.a, self.b)

    def __str__(self):
        """op.__str__() <==> str(op)."""
        return "{}*x + {}*y".format(self.a, self.b)


class MultiplyOperator(LinearOperator):

    """Operator multiplying two elements.

    The multiply operator calculates:

    outp = inp[0] * inp[1]

    This is only applicable in Algebras.
    """

    # pylint: disable=abstract-method
    def __init__(self, space):
        """Initialize a MultiplyOperator instance.

        Parameters
        ----------
        space : LinearSpace
            The space of elements which the operator is acting on
        """
        self.domain = CartesianProduct(space, space)
        self.range = space

    def _apply(self, inp, outp):
        """Multiply the input and write to output.

        Parameters
        ----------
        inp : domain element
            An element in the operator domain (2-tuple of space
            elements) whose elementwise product is calculated
        outp : range element
            Vector to which the result is written

        Examples
        --------
        >>> from odl.space.cartesian import Rn
        >>> r3 = Rn(3)
        >>> x = r3.element([1, 2, 3])
        >>> y = r3.element([1, 2, 3])
        >>> z = r3.element()
        >>> op = MultiplyOperator(r3)
        >>> op([x, y], z)
        Rn(3).element([1.0, 4.0, 9.0])
        >>> z
        Rn(3).element([1.0, 4.0, 9.0])
        """
        outp.space.multiply(outp, inp[0], inp[1])

    def __repr__(self):
        """op.__repr__() <==> repr(op)."""
        return 'MultiplyOperator({!r})'.format(self.range)

    def __str__(self):
        """op.__str__() <==> str(op)."""
        return "x * y"


if __name__ == '__main__':
    from doctest import testmod, NORMALIZE_WHITESPACE
    testmod(optionflags=NORMALIZE_WHITESPACE)