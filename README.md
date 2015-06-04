# ActiveMQ Broker Monitoring (Version 1.0)


# Description
This field pack is a python script that collects data from remote Active MQ broker JMX interface (via Jolokia http) and publishes to EPA using 9.7.1 Restful EPAgent

## Releases
From time to time, projects may make compiled releases available.  While source code is always available for complete build, releases serve as a "tag" (numbered release) and often contain prepared packages that are prebuilt and ready to use.  Visit `http://github.com/ca-apm/<repo_name>/releases` for details.

## APM version
APM 9.7.1

## Supported third party versions
Apache ActiveMQ 5.10.1

## Limitations
This field pack currently only supports connections to one ActiveMQ broker.

## License
[Apache License, Version 2.0, January 2004](http://www.apache.org/licenses/). See [Licensing](https://communities.ca.com/docs/DOC-231150910#license) on the CA APM Developer Community.

# Installation Instructions

## Prerequisites
* Install, configure and run an EPAgent on the same or a remote server. See [CA APM Environment Performance Agent Implementation Guide](https://wiki.ca.com/display/APMDEVOPS97/CA+APM+Environment+Performance+Agent+Implementation+Guide).
* Python 2.7 or above with the 'requests' python package This can be obtained in one of the following ways: `yum install python-requests` or `pip install requests` or `easy_install requests`
* JMX and Jolokia enabled and access not restricted on ActiveMQ broker

## Dependencies
APM EPAgent version 9.7.1

## Installation
Copy `activeMQ.py` to any diretory and make it runnable (`chmod u+x activeMQ.py`)

## Configuration
n/a

# Usage Instructions
```Usage: activeMQ.py [options]

Options:
  -h, --help show this help message and exit
  -v, --verbose verbose output
  -H HOSTNAME, --hostname=HOSTNAME
    hostname EPAgent is running on
  -p PORT, --port=PORT port EPAgent is connected to
  -m METRICPATH, --metric_path=METRICPATH
     metric path header for all metrics
  -u USER:PASSWORD, --user=USER:PASSWORD
     user and password for ActiveMQ JMX access
  -b BROKERHOSTNAME, --broker=BROKERHOSTNAME
     hostname of ActiveMQ broker
  -j JMX_PORT, --jmx_port=JMX_PORT
     JMX port of ActiveMQ broker```

## Metric description
The field pack queries the JMX API of AtiveMQ an provides information about the broker, queues and topics.

## Custom Management Modules
n/a

## Custom type viewers
A type viewer `activemqepa.typeviewers.xml` is included in the project. it matches against the metric path `ActiveMQ|<hostname>|Broker|<brokername>`

## Name Formatter Replacements
n/a

## Debugging and Troubleshooting
You can run the python script with option -v for verbose output. You can also uncomment the `print` statements in the code.

## Support
This document and associated tools are made available from CA Technologies as examples and provided at no charge as a courtesy to the CA APM Community at large. This resource may require modification for use in your environment. However, please note that this resource is not supported by CA Technologies, and inclusion in this site should not be construed to be an endorsement or recommendation by CA Technologies. These utilities are not covered by the CA Technologies software license agreement and there is no explicit or implied warranty from CA Technologies. They can be used and distributed freely amongst the CA APM Community, but not sold. As such, they are unsupported software, provided as is without warranty of any kind, express or implied, including but not limited to warranties of merchantability and fitness for a particular purpose. CA Technologies does not warrant that this resource will meet your requirements or that the operation of the resource will be uninterrupted or error free or that any defects will be corrected. The use of this resource implies that you understand and agree to the terms listed herein.

Although these utilities are unsupported, please let us know if you have any problems or questions by adding a comment to the CA APM Community Site area where the resource is located, so that the Author(s) may attempt to address the issue or question.

Unless explicitly stated otherwise this field pack is only supported on the same platforms as the APM core agent. See [APM Compatibility Guide](http://www.ca.com/us/support/ca-support-online/product-content/status/compatibility-matrix/application-performance-management-compatibility-guide.aspx).


# Contributing
The [CA APM Community](https://communities.ca.com/community/ca-apm) is the primary means of interfacing with other users and with the CA APM product team.  The [developer subcommunity](https://communities.ca.com/community/ca-apm/ca-developer-apm) is where you can learn more about building APM-based assets, find code examples, and ask questions of other developers and the CA APM product team.

If you wish to contribute to this or any other project, please refer to [easy instructions](https://communities.ca.com/docs/DOC-231150910) available on the CA APM Developer Community.


# Change log
Changes for each version of the field pack.

Version | Author | Comment
--------|--------|--------
1.0 | Guenter Grossberger | First version of the field pack.
