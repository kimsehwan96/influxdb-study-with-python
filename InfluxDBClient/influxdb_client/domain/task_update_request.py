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


class TaskUpdateRequest(object):
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
        'status': 'TaskStatusType',
        'flux': 'str',
        'name': 'str',
        'every': 'str',
        'cron': 'str',
        'offset': 'str',
        'description': 'str'
    }

    attribute_map = {
        'status': 'status',
        'flux': 'flux',
        'name': 'name',
        'every': 'every',
        'cron': 'cron',
        'offset': 'offset',
        'description': 'description'
    }

    def __init__(self, status=None, flux=None, name=None, every=None, cron=None, offset=None, description=None):  # noqa: E501,D401,D403
        """TaskUpdateRequest - a model defined in OpenAPI."""  # noqa: E501
        self._status = None
        self._flux = None
        self._name = None
        self._every = None
        self._cron = None
        self._offset = None
        self._description = None
        self.discriminator = None

        if status is not None:
            self.status = status
        if flux is not None:
            self.flux = flux
        if name is not None:
            self.name = name
        if every is not None:
            self.every = every
        if cron is not None:
            self.cron = cron
        if offset is not None:
            self.offset = offset
        if description is not None:
            self.description = description

    @property
    def status(self):
        """Get the status of this TaskUpdateRequest.

        :return: The status of this TaskUpdateRequest.
        :rtype: TaskStatusType
        """  # noqa: E501
        return self._status

    @status.setter
    def status(self, status):
        """Set the status of this TaskUpdateRequest.

        :param status: The status of this TaskUpdateRequest.
        :type: TaskStatusType
        """  # noqa: E501
        self._status = status

    @property
    def flux(self):
        """Get the flux of this TaskUpdateRequest.

        The Flux script to run for this task.

        :return: The flux of this TaskUpdateRequest.
        :rtype: str
        """  # noqa: E501
        return self._flux

    @flux.setter
    def flux(self, flux):
        """Set the flux of this TaskUpdateRequest.

        The Flux script to run for this task.

        :param flux: The flux of this TaskUpdateRequest.
        :type: str
        """  # noqa: E501
        self._flux = flux

    @property
    def name(self):
        """Get the name of this TaskUpdateRequest.

        Override the 'name' option in the flux script.

        :return: The name of this TaskUpdateRequest.
        :rtype: str
        """  # noqa: E501
        return self._name

    @name.setter
    def name(self, name):
        """Set the name of this TaskUpdateRequest.

        Override the 'name' option in the flux script.

        :param name: The name of this TaskUpdateRequest.
        :type: str
        """  # noqa: E501
        self._name = name

    @property
    def every(self):
        """Get the every of this TaskUpdateRequest.

        Override the 'every' option in the flux script.

        :return: The every of this TaskUpdateRequest.
        :rtype: str
        """  # noqa: E501
        return self._every

    @every.setter
    def every(self, every):
        """Set the every of this TaskUpdateRequest.

        Override the 'every' option in the flux script.

        :param every: The every of this TaskUpdateRequest.
        :type: str
        """  # noqa: E501
        self._every = every

    @property
    def cron(self):
        """Get the cron of this TaskUpdateRequest.

        Override the 'cron' option in the flux script.

        :return: The cron of this TaskUpdateRequest.
        :rtype: str
        """  # noqa: E501
        return self._cron

    @cron.setter
    def cron(self, cron):
        """Set the cron of this TaskUpdateRequest.

        Override the 'cron' option in the flux script.

        :param cron: The cron of this TaskUpdateRequest.
        :type: str
        """  # noqa: E501
        self._cron = cron

    @property
    def offset(self):
        """Get the offset of this TaskUpdateRequest.

        Override the 'offset' option in the flux script.

        :return: The offset of this TaskUpdateRequest.
        :rtype: str
        """  # noqa: E501
        return self._offset

    @offset.setter
    def offset(self, offset):
        """Set the offset of this TaskUpdateRequest.

        Override the 'offset' option in the flux script.

        :param offset: The offset of this TaskUpdateRequest.
        :type: str
        """  # noqa: E501
        self._offset = offset

    @property
    def description(self):
        """Get the description of this TaskUpdateRequest.

        An optional description of the task.

        :return: The description of this TaskUpdateRequest.
        :rtype: str
        """  # noqa: E501
        return self._description

    @description.setter
    def description(self, description):
        """Set the description of this TaskUpdateRequest.

        An optional description of the task.

        :param description: The description of this TaskUpdateRequest.
        :type: str
        """  # noqa: E501
        self._description = description

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
        if not isinstance(other, TaskUpdateRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return true if both objects are not equal."""
        return not self == other