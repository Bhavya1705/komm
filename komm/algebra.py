import functools

import numpy as np

from .util import \
    int2binlist, binlist2int

__all__ = ['BinaryPolynomial', 'BinaryFiniteExtensionField']


class BinaryPolynomial(int):
    """
    Binary polynomial.

    A *binary polynomial* is a polynomial whose coefficients are elements in the finite field
    :math:`\\mathbb{F}_2 = \\{ 0, 1 \\}`.  The default constructor takes an :obj:`int` as input,
    whose binary digits represent the coefficients of the polynomial---the leftmost bit standing
    for the highest degree term.  For example, the integer :code:`0b11010` = :code:`0o32` =
    :code:`26` represents the polynomial :math:`X^4 + X^3 + X`.

    There are two alternative constructors for this class, the class methods
    :func:`from_coefficients` and :func:`from_exponents`.  See their documentation for details.

    This class supports addition, multiplication, and division of polynomials.

    Examples
    ========
    >>> poly = komm.BinaryPolynomial(0b11010)  # X^4 + X^3 + X
    >>> poly
    0b11010

    >>> poly1 = komm.BinaryPolynomial(0b10100)  # X^4 + X^2
    >>> poly2 = komm.BinaryPolynomial(0b11010)  # X^4 + X^3 + X
    >>> poly1 + poly2  # X^3 + X^2 + X
    0b1110
    >>> poly1 * poly2  # X^8 + X^7 + X^6 + X^3
    0b111001000
    >>> poly1**2  # X^8 + X^4
    0b100010000
    """

    @classmethod
    def from_coefficients(cls, coefficients):
        """
        Constructs a BinaryPolynomial from an :obj:`ndarray` (or :obj:`list`)
        of :obj:`int` representing the coefficients of the polynomial---the
        :math:`i`-th element of the array standing for the coefficient of
        :math:`X^i`.  For example, :code:`[0, 1, 0, 1, 1]` represents the
        polynomial :math:`X^4 + X^3 + X`.

        Examples
        ========
        >>> komm.BinaryPolynomial.from_coefficients([0, 1, 0, 1, 1])  # X^4 + X^3 + X
        0b11010
        """
        return cls(binlist2int(coefficients))

    @classmethod
    def from_exponents(cls, exponents):
        """
        Constructs a BinaryPolynomial from an :obj:`ndarray` (or :obj:`list`)
        of :obj:`int` representing the exponents of the nonzero terms of the
        polynomial.  For example, :code:`[1, 3, 4]` represents the polynomial
        :math:`X^4 + X^3 + X`.

        Examples
        ========
        >>> komm.BinaryPolynomial.from_exponents([1, 3, 4])  # X^4 + X^3 + X
        0b11010
        """
        return cls(binlist2int(np.bincount(exponents)))

    def coefficients(self, width=None):
        """
        Returns the coefficients of the polynomial as an :obj:`ndarray` of
        :obj:`int`.  The :math:`i`-th element of the array stands for the
        coefficient of :math:`X^i`.

        Parameters
        ==========
        width : :obj:`int`, optional
            If this parameter is specified, the output will be filled with zeros
            on the right so that the its length will be the specified value.

        Examples
        ========
        >>> poly = komm.BinaryPolynomial(0b11010)  # X^4 + X^3 + X
        >>> poly.coefficients()
        array([0, 1, 0, 1, 1])
        >>> poly.coefficients(width=8)
        array([0, 1, 0, 1, 1, 0, 0, 0])
        """
        return np.array(int2binlist(self, width=width), dtype=np.int)

    def exponents(self):
        """
        Returns the exponents of the nonzero terms of the polynomial as an
        :obj:`ndarray` of :obj:`int`.  The exponents are returned in ascending
        order.

        Examples
        ========
        >>> poly = komm.BinaryPolynomial(0b11010)  # X^4 + X^3 + X
        >>> poly.exponents()
        array([1, 3, 4])
        """
        return np.flatnonzero(self.coefficients())

    @property
    def degree(self):
        """
        The degree of the polynomial.

        Examples
        ========
        >>> poly = komm.BinaryPolynomial(0b11010)  # X^4 + X^3 + X
        >>> poly.degree
        4
        """
        return self.bit_length() - 1

    def __lshift__(self, n):
        return self.__class__(super().__lshift__(n))

    def __rshift__(self, n):
        return self.__class__(super().__rshift__(n))

    def __add__(self, other):
        return self.__class__(super().__xor__(other))

    def __sub__(self, other):
        return self.__class__(super().__xor__(other))

    def __mul__(self, other):
        return self.from_coefficients(np.convolve(self.coefficients(), other.coefficients()) % 2)

    def __pow__(self, exponent):
        return power(self.__class__, self, exponent)

    @functools.lru_cache(maxsize=None)
    def __divmod__(self, den):
        div, mod = self.__class__(0), self
        d = mod.bit_length() - den.bit_length()
        while d >= 0:
            div += (1 << d)
            mod += (den << d)
            d = mod.bit_length() - den.bit_length()
        return div, mod

    def __floordiv__(self, other):
        return self.__divmod__(other)[0]

    def __mod__(self, other):
        return self.__divmod__(other)[1]

#    @functools.lru_cache(maxsize=None)
    def evaluate(self, point):
        """
        Returns the polynomial evaluated at a given point. See XXX

        Parameters
        ==========
        point
            Any Python object supporting the operations of addition,
            subtraction, and multiplication.

        Examples
        ========
        >>> poly = komm.BinaryPolynomial(0b11010)  # X^4 + X^3 + X
        >>> poly.evaluate(7)  # same as 7**4 + 7**3 + 7
        2751
        >>> point = np.array([[1, 2], [3, 4]])
        >>> poly.evaluate(point)  # same as point**4 + point**3 + point
        array([[  3,  26],
               [111, 324]])
        """
        return binary_horner(self, point)

    def __repr__(self):
        return bin(self)

    def __str__(self):
        return bin(self)

    @classmethod
    def xgcd(cls, poly1, poly2):
        """
        Performs the extended Euclidean algorithm with poly1 and poly2. See XXX
        """
        return xgcd(cls, poly1, poly2)


class BinaryFiniteExtensionField:
    """
    Galois field with binary characteristic.

    Objects of this class represent a *finite field* :math:`\\mathrm{GF}(2^k)`,
    with *characteristic* :math:`2` and *degree* :math:`k`.  The constructor
    takes :math:`k` as a parameter.  Optionally, the *modulus*, or *primitive polynomial*,
    :math:`p(X)` may be specified; if not, the following default values will be chosen
    :cite:`Lin.Costello.04` (p. 42):

    ===========   ==============  ===========   =====================
     :math:`k`     :math:`p(X)`    :math:`k`     :math:`p(X)`
    ===========   ==============  ===========   =====================
     1             0o11            9             0b1000010001
     2             0b111           10            0b10000001001
     3             0b1011          11            0b100000000101
     4             0b10011         12            0b1000001010011
     5             0b100101        13            0b10000000011011
     6             0b1000011       14            0b100010001000011
     7             0b10001001      15            0b1000000000000011
     8             0b100011101     16            0b10001000000001011
    ===========   ==============  ===========   =====================

    To construct *elements* of the finite field, call the finite field object.  For example,
    :code:`field(0b1101)` will construct the element whose polynomial representation is
    :math:`X^3 + X^2 + 1`.

    Parameters
    ==========
    degree : :obj:`int`
        The degree :math:`k` of the finite field. Must be a positive integer.
    modulus : :obj:`int` or :obj:`BinaryPolynomial`, optional
        The modulus (primitive polynomial) of the field. Must be an irreducible polynomial.

    Examples
    ========
    >>> field = BinaryFiniteExtensionField(4)
    >>> field
    BinaryFiniteExtensionField(4)
    >>> (field.characteristic, field.degree)
    (2, 4)
    >>> field.modulus
    0b10011

    >>> field1 = BinaryFiniteExtensionField(3)
    >>> alpha1 = field1.primitive_element
    >>> [alpha1**i for i in range(7)]
    [0b1, 0b10, 0b100, 0b11, 0b110, 0b111, 0b101]
    >>> field2 = BinaryFiniteExtensionField(3, modulus=0b1101)
    >>> alpha2 = field2.primitive_element
    >>> [alpha2**i for i in range(7)]
    [0b1, 0b10, 0b100, 0b101, 0b111, 0b11, 0b110]

    >>> field = BinaryFiniteExtensionField(4)
    >>> x = field(0b1011)
    >>> y = field(0b1100)
    >>> x + y
    0b111
    >>> x * y
    0b1101
    >>> x / y
    0b10
    """
    def __init__(self, degree, modulus=None):
        self._characteristic = 2
        self._degree = degree
        if modulus is None:
            PRIMITIVE_POLYNOMIALS = {
                 1: 0b11,
                 2: 0b111,
                 3: 0b1011,
                 4: 0b10011,
                 5: 0b100101,
                 6: 0b1000011,
                 7: 0b10001001,
                 8: 0b100011101,
                 9: 0b1000010001,
                10: 0b10000001001,
                11: 0b100000000101,
                12: 0b1000001010011,
                13: 0b10000000011011,
                14: 0b100010001000011,
                15: 0b1000000000000011,
                16: 0b10001000000001011}
            self._modulus = BinaryPolynomial(PRIMITIVE_POLYNOMIALS[degree])
        else:
            self._modulus = BinaryPolynomial(modulus)

        assert self._modulus.degree == self._degree

    @property
    def characteristic(self):
        """
        The characteristic :math:`2` of the finite field.
        """
        return self._characteristic

    @property
    def degree(self):
        """
        The degree :math:`k` of the finite field.
        """
        return self._degree

    @property
    def modulus(self):
        """
        The modulus (primitive polynomial) of the field.
        """
        return self._modulus

    @property
    def order(self):
        """
        The order (number of elements) of the finite field, given by :math:`2^k`.
        """
        return 2 ** self._degree

    @property
    def primitive_element(self):
        """
        A primitive element :math:`\\alpha` of the finite field, satisfying :math:`p(\\alpha) = 0`,
        where :math:`p(X)` is the modulus (primitive polynomial) of the finite field.
        """
        return self(2)

    @functools.lru_cache(maxsize=None)
    def multiply(self, x, y):
        return self((BinaryPolynomial(x) * BinaryPolynomial(y)) % self._modulus)

    @functools.lru_cache(maxsize=None)
    def inverse(self, x):
        d, s, _ = BinaryPolynomial.xgcd(BinaryPolynomial(x), self._modulus)
        if d == 1:
            return self(s)
        else:
            raise ZeroDivisionError('This element does not have a multiplicative inverse')

    @functools.lru_cache(maxsize=None)
    def logarithm(self, x, base=None):
        if base is None:
            base = self.primitive_element
        for i in range(self.order):
            if base**i == x:
                return i
        return -1

    def power(self, x, exponent):
        if exponent < 0:
            return power(self, self.inverse(x), -exponent)
        else:
            return power(self, x, exponent)

    @staticmethod
    def conjugates(x):
        """
        Returns the conjugates of :code:`x` :cite:`Lin.Costello.04` (Sec. 2.5).
        """
        conjugate_list = []
        exponent = 0
        while True:
            y = x**(2**exponent)
            if y not in conjugate_list:
                conjugate_list.append(y)
            else:
                break
            exponent += 1
        return conjugate_list

    @staticmethod
    def minimal_polynomial(x):
        """
        Returns the minimal polynomial of :code:`x` :cite:`Lin.Costello.04` (Sec. 2.5).
        """
        one = x.field(1)
        monomials = [np.array([y, one], dtype=np.object) for y in x.conjugates()]
        coefficients = functools.reduce(np.convolve, monomials)
        return BinaryPolynomial.from_coefficients(int(c) for c in coefficients)

    def __repr__(self):
        args = '{}'.format(self._degree)
        return '{}({})'.format(self.__class__.__name__, args)

    def __call__(self, value):
        """
        Constructs elements of the finite field.
        """
        element = self._Element(value)
        element.field = self
        return element

    class _Element(int):
        """
        Elements of a BinaryFiniteExtensionField.

        Objects of this class represents *elements* of the finite field :math:`\\mathrm{GF}(2^k)`.
        """
        def __eq__(self, other): return int(self) == int(other) and self.field._modulus == other.field._modulus
        def __hash__(self): return hash((int(self), self.field._modulus))
        def __add__(self, other): return self.field(self ^ other)
        def __sub__(self, other): return self.field(self ^ other)
        def __mul__(self, other): return self.field.multiply(self, other)
        def inverse(self): return self.field.inverse(self)
        def __truediv__(self, other): return self * other.inverse()
        def logarithm(self, base=None): return self.field.logarithm(self, base)
        def __pow__(self, exponent): return self.field.power(self, exponent)
        def conjugates(self): return self.field.conjugates(self)
        def minimal_polynomial(self): return self.field.minimal_polynomial(self)
        def __repr__(self): return bin(self)
        def __str__(self): return bin(self)







def xgcd(ring, x, y):
    """
    Performs the `extended Euclidean algorithm
    <https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm>`_ with :code:`x` and :code:`y`.
    """
    if x == 0:
        return y, ring(0), ring(1)
    else:
        d, s, t = xgcd(ring, y % x, x)
        return d, t - s * (y // x), s


def power(ring, x, n):
    """
    Returns :code:`x**n` using the `exponentiation by squaring
    <https://en.wikipedia.org/wiki/Exponentiation_by_squaring>`_ algorithm.
    """
    if n == 0:
        return ring(1)
    elif n == 1:
        return x
    elif n % 2 == 0:
        return power(ring, x * x, n // 2)
    else:
        return x * power(ring, x * x, n // 2)


def binary_horner(poly, x):
    """
    Returns the binary polynomial :code:`poly` evaluated at point :code:`x`, using `Horner's
    method <https://en.wikipedia.org/wiki/Horner's_method>`_.  Any Python object supporting
    the operations of addition, subtraction, and multiplication may serve as the input point.
    """
    result = x - x  # zero
    for coefficient in reversed(poly.coefficients()):
        result *= x
        if coefficient:
            result += coefficient
    return result


def rref(M):
    """
    Computes the row-reduced echelon form of the matrix M modulo 2.

    Loosely based on
    [1] https://gist.github.com/rgov/1499136

    """
    M_rref = np.copy(M)

    def pivot(row):
        f_list = np.flatnonzero(row)
        if f_list.size > 0:
            return f_list[0]
        else:
            return None

    for r in range(M_rref.shape[0]):
        # Choose the pivot.
        possible_pivots = [pivot(row) for row in M_rref[r:]]
        p = np.argmin(possible_pivots) + r

        # Swap rows.
        M_rref[[r, p]] = M_rref[[p, r]]

        # Pivot column.
        f = pivot(M_rref[r])

        # Subtract the row from others.
        for i in range(M_rref.shape[0]):
            if i != r and M_rref[i, f] != 0:
                M_rref[i] = (M_rref[i] + M_rref[r]) % 2

    return M_rref


# TODO: this should be the main function!
#       rref should call this instead
def xrref(M):
    """
    Computes the row-reduced echelon form of the matrix M modulo 2.

    Returns
    =======
    P

    M_rref

    pivots

    Such that :obj:`M_rref = P @ M` (where :obj:`@` stands for matrix multiplication).

    Loosely based on
    [1] https://gist.github.com/rgov/1499136

    """
    eye = np.eye(M.shape[0], dtype=np.int)

    augmented_M = np.concatenate((np.copy(M), np.copy(eye)), axis=1)
    augmented_M_rref = rref(augmented_M)
    M_rref = augmented_M_rref[:, :M.shape[1]]
    P = augmented_M_rref[:, M.shape[1]:]

    pivots = []
    j = 0
    while len(pivots) < M_rref.shape[0]:
        if np.array_equal(M_rref[:, j], eye[len(pivots)]):
            pivots.append(j)
        j += 1

    return P, M_rref, np.array(pivots)


def right_inverse(M):
    """
    """
    M_rref_ri = np.zeros(M.T.shape, dtype=np.int)
    P, _, s_indices = xrref(M)
    M_rref_ri[s_indices] = np.eye(M.shape[0])
    M_ri = np.dot(M_rref_ri, P) % 2
    return M_ri


def null_matrix(M):
    """
    """
    (k, n) = M.shape
    P, M_rref, s_indices = xrref(M)
    N = np.empty((n - k, n), dtype=np.int)
    p_indices = np.setdiff1d(np.arange(M.shape[1]), s_indices)
    N[:, p_indices] = np.eye(n - k, dtype=np.int)
    N[:, s_indices] = M_rref[:, p_indices].T
    return N