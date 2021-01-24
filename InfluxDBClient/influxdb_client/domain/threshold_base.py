# coding: utf-8

"""
Influx API Service.

No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

OpenAPI spec version: 0.1.0
Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class ThresholdBase(object):
    """NOTE: This class is auto generated by OpenAPI Generator.

    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'level': 'CheckStatusLevel',
        'all_values': 'bool'
    }

    attribute_map = {
        'level': 'level',
        'all_values': 'allValues'
    }

    def __init__(self, level=None, all_values=None):  # noqa: E501,D401,D403
        """ThresholdBase - a model defined in OpenAPI."""  # noqa: E501
        self._level = None
        self._all_values = None
        self.discriminator = None

        if level is not None:
            self.level = level
        if all_values is not None:
            self.all_values = all_values

    @property
    def level(self):
        """Get the level of this ThresholdBase.

        :return: The level of this ThresholdBase.
        :rtype: CheckStatusLevel
        """  # noqa: E501
        return self._level

    @level.setter
    def level(self, level):
        """Set the level of this ThresholdBase.

        :param level: The level of this ThresholdBase.
        :type: CheckStatusLevel
        """  # noqa: E501
        self._level = level

    @property
    def all_values(self):
        """Get the all_values of this ThresholdBase.

        If true, only alert if all values meet threshold.

        :return: The all_values of this ThresholdBase.
        :rtype: bool
        """  # noqa: E501
        return self._all_values

    @all_values.setter
    def all_values(self, all_values):
        """Set the all_values of this ThresholdBase.

        If true, only alert if all values meet threshold.

        :param all_values: The all_values of this ThresholdBase.
        :type: bool
        """  # noqa: E501
        self._all_values = all_values

    def to_dict(self):
        """Return the model properties as a dict."""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Return the string representation of the model."""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`."""
        return self.to_str()

    def __eq__(self, other):
        """Return true if both objects are equal."""
        if not isinstance(other, ThresholdBase):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return true if both objects are not equal."""
        return not self == other