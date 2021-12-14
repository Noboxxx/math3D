import math


class Vector3(object):

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

        magnitude = self.magnitude
        if magnitude <= 0.0:
            raise ValueError('magnitude is equal or less than 0.0 -> {}'.format(magnitude))

    def __repr__(self):
        return '{}.{}(x={}, y={}, z={})'.format(self.__class__.__module__, self.__class__.__name__, self.x, self.y, self.z)

    def __iter__(self):
        return iter(self.astuple())

    def __mul__(self, other):
        """
        multiply a vector by a number
        """
        if isinstance(other, (float, int)):
            result = [other * v for v in self.astuple()]
            return self.__class__(*result)
        raise TypeError(str(type(other)))

    def __add__(self, other):
        """
        Add two vectors together
        """
        if isinstance(other, self.__class__):
            result = [va + vb for va, vb in zip(self.astuple(), other.astuple())]
            return self.__class__(*result)
        raise TypeError(str(type(other)))

    # Magnitude

    @property
    def magnitude(self):
        return math.sqrt(self.x ** 2.0 + self.y ** 2.0 + self.z ** 2.0)

    def setMagnitude(self, value):
        ratio = value / self.magnitude
        self.x *= ratio
        self.y *= ratio
        self.z *= ratio

    # Normalize

    def normalized(self):
        vectorCopy = self.copy()
        vectorCopy.normalize()
        return vectorCopy

    def normalize(self):
        """
        scale vector to a magnitude of one
        """
        magnitude = self.magnitude
        self.x /= magnitude
        self.y /= magnitude
        self.z /= magnitude

    # Convert

    def astuple(self):
        return self.x, self.y, self.z

    def copy(self):
        return self.__class__(self.x, self.y, self.z)


class Matrix(object):

    def __init__(
            self,
            xx=1.0, xy=0.0, xz=0.0, xw=0.0,
            yx=0.0, yy=1.0, yz=0.0, yw=0.0,
            zx=0.0, zy=0.0, zz=1.0, zw=0.0,
            px=0.0, py=0.0, pz=0.0, pw=1.0,
    ):
        self.xx = float(xx)
        self.xy = float(xy)
        self.xz = float(xz)
        self.xw = float(xw)

        self.yx = float(yx)
        self.yy = float(yy)
        self.yz = float(yz)
        self.yw = float(yw)

        self.zx = float(zx)
        self.zy = float(zy)
        self.zz = float(zz)
        self.zw = float(zw)

        self.px = float(px)
        self.py = float(py)
        self.pz = float(pz)
        self.pw = float(pw)

    def __repr__(self):
        return '<{}.{}: {}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.aslist(),
        )

    def __iter__(self):
        return iter(self.aslist())

    def aslist(self):
        return (
            self.xx,
            self.xy,
            self.xz,
            self.xw,
            self.yx,
            self.yy,
            self.yz,
            self.yw,
            self.zx,
            self.zy,
            self.zz,
            self.zw,
            self.px,
            self.py,
            self.pz,
            self.pw,
        )

    def rows(self):
        return (
            (self.xx, self.xy, self.xz, self.xw),
            (self.yx, self.yy, self.yz, self.yw),
            (self.zx, self.zy, self.zz, self.zw),
            (self.px, self.py, self.pz, self.pw),
        )

    def columns(self):
        return (
            (self.xx, self.yx, self.zx, self.px),
            (self.xy, self.yy, self.zy, self.py),
            (self.xz, self.yz, self.zz, self.pz),
            (self.xw, self.yw, self.zw, self.pw),
        )

    def copy(self):
        return self.__class__(*self.aslist())

    def mirrored(self, mirrorAxis='x'):  # type: (basestring) -> Matrix
        matrixCopy = self.copy()
        matrixCopy.mirror(mirrorAxis)
        return matrixCopy

    def mirror(self, mirrorAxis='x'):  # type: (basestring) -> None
        if mirrorAxis == 'x':
            self.xx *= -1
            self.yx *= -1
            self.zx *= -1
            self.px *= -1

        elif mirrorAxis == 'y':
            self.xy *= -1
            self.yy *= -1
            self.zy *= -1
            self.py *= -1

        elif mirrorAxis == 'z':
            self.xz *= -1
            self.yz *= -1
            self.zz *= -1
            self.pz *= -1

        else:
            raise ValueError('Unrecognized mirror axis -> {}'.format(mirrorAxis))

    def normalized(self):
        raise NotImplementedError

    def normalize(self):
        raise NotImplementedError

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            newMatrix = list()
            for column in self.rows()[:3]:
                for row in other.columns()[:3]:
                    result = 0
                    for c, r in zip(column, row):
                        result += c * r
                    newMatrix.append(result)
                newMatrix.append(0.0)
            newMatrix.append(self.px + other.px)
            newMatrix.append(self.py + other.py)
            newMatrix.append(self.pz + other.pz)
            newMatrix.append(1.0)
            return self.__class__(*newMatrix)
        raise TypeError(
            'cannot do \'{}\' * \'{}\''.format(
                str(self.__class__),
                str(type(other)),
            )
        )


def test():
    from maya import cmds

    cmds.delete(cmds.ls('locator*'))

    def blendValues(a, b, blender):
        return (1.0 - blender) * a + blender * b

    def createLocator(vector):
        lct = cmds.spaceLocator()
        cmds.xform(lct, translation=vector.astuple())
        cmds.xform(lct, scale=(.1, .1, .1))

    def blendVectors(va, vb, blender):
        resultVector = Vector3(
            x=blendValues(va.x, vb.x, blender),
            y=blendValues(va.y, vb.y, blender),
            z=blendValues(va.z, vb.z, blender),
        )

        blendedMagnitude = blendValues(va.magnitude, vb.magnitude, blender)

        resultVector.setMagnitude(blendedMagnitude)
        return resultVector

    va = Vector3(0, 2, 0)
    vb = Vector3(1, 0, 0)

    for index in range(1, 10):
        blender = index / 10.0
        vector = blendVectors(va, vb, blender)
        print 'blender', blender, 'magnitude', vector.magnitude
        createLocator(vector)


def test2():
    from maya.api import OpenMaya
    from maya import cmds

    def createLocator(matrix):
        lct = cmds.spaceLocator()
        cmds.xform(lct, matrix=list(matrix))

    try:
        cmds.delete('locator3')
    except:
        pass

    obj1 = 'locator1'
    obj2 = 'locator2'

    m1 = OpenMaya.MMatrix(cmds.getAttr('{}.worldMatrix'.format(obj1)))
    m2 = OpenMaya.MMatrix(cmds.getAttr('{}.worldInverseMatrix'.format(obj2)))

    createLocator(m1 * m2)
