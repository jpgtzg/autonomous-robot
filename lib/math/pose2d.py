import math
from dataclasses import dataclass
from typing import List, TypeVar
from .translation2d import Translation2d
from .rotation2d import Rotation2d
from .twist2d import Twist2d

# Define TypeVar for interpolation
T = TypeVar('T', bound='Pose2d')

@dataclass
class Pose2d:
    translation: Translation2d
    rotation: Rotation2d

    def __init__(self, x: float = 0.0, y: float = 0.0, rotation: Rotation2d = None):
        if rotation is None:
            rotation = Rotation2d(0.0)
        self.translation = Translation2d(x, y)
        self.rotation = rotation

    def plus(self, other: 'Transform2d') -> 'Pose2d':
        new_translation = self.translation.plus(other.m_translation.rotate_by(self.rotation))
        new_rotation = other.m_rotation.plus(self.rotation)
        return Pose2d(new_translation.x, new_translation.y, new_rotation)

    def minus(self, other: 'Pose2d') -> 'Transform2d':
        relative_pose = self.relative_to(other)
        return Transform2d(relative_pose.translation, relative_pose.rotation)

    def relative_to(self, other: 'Pose2d') -> 'Pose2d':
        transform = Transform2d(other.translation, other.rotation)  # Assuming a constructor
        return Pose2d(transform.translation.x, transform.translation.y, transform.rotation)

    def get_translation(self) -> Translation2d:
        return self.translation

    def get_x(self) -> float:
        return self.translation.x

    def get_y(self) -> float:
        return self.translation.y

    def get_rotation(self) -> Rotation2d:
        return self.rotation

    def rotate_by(self, rotation: Rotation2d) -> 'Pose2d':
        return Pose2d(self.translation.rotate_by(rotation), self.rotation.rotate_by(rotation))

    def exp(self, twist: Twist2d) -> 'Pose2d':
        dx = twist.dx
        dy = twist.dy
        dtheta = twist.dtheta

        sin_theta = math.sin(dtheta)
        cos_theta = math.cos(dtheta)

        if abs(dtheta) < 1E-9:
            s = 1.0 - 1.0 / 6.0 * dtheta * dtheta
            c = 0.5 * dtheta
        else:
            s = sin_theta / dtheta
            c = (1 - cos_theta) / dtheta

        transform = Transform2d(
            Translation2d(dx * s - dy * c, dx * c + dy * s),
            Rotation2d(math.atan2(sin_theta, cos_theta))
        )

        return self.plus(transform)
    
class Transform2d:
    """Represents a transformation for a Pose2d in the pose's frame."""

    def __init__(self, translation=None, rotation=None):
        """
        Constructs the identity transform or a transform with given components.
        
        :param translation: Translation2d object for the transformation.
        :param rotation: Rotation2d object for the transformation.
        """
        if translation is None:
            self.m_translation = Translation2d()
            self.m_rotation = Rotation2d()
        else:
            self.m_translation = translation
            self.m_rotation = rotation

    @classmethod
    def from_poses(cls, initial, last):
        """
        Constructs the transform that maps the initial pose to the final pose.
        
        :param initial: The initial Pose2d for the transformation.
        :param last: The final Pose2d for the transformation.
        :return: A Transform2d object representing the transformation.
        """
        translation = last.get_translation().minus(initial.get_translation())
        rotation = last.get_rotation().minus(initial.get_rotation())
        rotated_translation = translation.rotate_by(initial.get_rotation().unary_minus())
        return cls(rotated_translation, rotation)

    @classmethod
    def from_coordinates(cls, x, y, rotation):
        """
        Constructs a transform with x and y translations instead of a separate Translation2d.
        
        :param x: The x component of the translational component of the transform.
        :param y: The y component of the translational component of the transform.
        :param rotation: The rotational component of the transform.
        :return: A Transform2d object.
        """
        translation = Translation2d(x, y)
        return cls(translation, rotation)

    def times(self, scalar):
        """
        Multiplies the transform by a scalar.
        
        :param scalar: The scalar.
        :return: A new Transform2d that is scaled.
        """
        return Transform2d(self.m_translation.times(scalar), self.m_rotation.times(scalar))

    def div(self, scalar):
        """
        Divides the transform by a scalar.
        
        :param scalar: The scalar.
        :return: A new Transform2d that is divided.
        """
        return self.times(1.0 / scalar)

    def plus(self, other):
        """
        Composes two transformations. The second transform is applied relative to the orientation of the first.
        
        :param other: The transform to compose with this one.
        :return: A new Transform2d that is the composition of the two transformations.
        """
        initial_pose = Pose2d()
        final_pose = initial_pose.transform_by(self).transform_by(other)
        return Transform2d.from_poses(initial_pose, final_pose)

    def get_translation(self):
        """Returns the translation component of the transformation."""
        return self.m_translation

    def get_x(self):
        """Returns the X component of the transformation's translation."""
        return self.m_translation.get_x()

    def get_y(self):
        """Returns the Y component of the transformation's translation."""
        return self.m_translation.get_y()

    def get_rotation(self):
        """Returns the rotational component of the transformation."""
        return self.m_rotation

    def inverse(self):
        """Inverts the transformation."""
        return Transform2d(
            self.get_translation().unary_minus().rotate_by(self.get_rotation().unary_minus()),
            self.get_rotation().unary_minus()
        )

    def __str__(self):
        return f"Transform2d({self.m_translation}, {self.m_rotation})"

    def __eq__(self, other):
        if isinstance(other, Transform2d):
            return (self.m_translation == other.m_translation and
                    self.m_rotation == other.m_rotation)
        return False

    def __hash__(self):
        return hash((self.m_translation, self.m_rotation))



# Note: You will need to implement the Translation2d, Rotation2d, and Pose2d classes as well for this
# code to function correctly. The methods called on these classes should match the functionality of 
# their Java counterparts.
