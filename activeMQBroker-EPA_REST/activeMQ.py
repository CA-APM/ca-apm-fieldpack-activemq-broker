#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
#note above line is for MacPorts python (with Requests module)
#!/usr/bin/env python

# This is a simple Collector Program who's intent is to demonstrate how
# we can collect simple Metrics and submit them to CA Wily via
# the RESTful interface that is part of the EPAgent.
#
# This script will collect system statistics via JMX from an ActiveMQ broker.
# The statistics are stored under the following groups:
#
# TODO
#       collectActiveMQ:
#           Calls the JMX interface of an ActiveMQ broker via the Jolokia http
#           interface.and reports broker, queue and topic statistics.
#
# The metrics will be default be reported under 'ActiveMQ|<hostname>|...'.  As
# multiple hosts can report to a single EPAgent's RESTful interace.  The inclusion
# the <hostname> in the metric path gives a opportunity to disambiguate those
# usages.
#
# Requirements:
#
#   This script requires the 'requests' python package in order to process the
#   RESTful queries.  This can be obtained in one of the following ways:
#
#       # yum install python-requests
#                   or
#       # pip install requests
#                   or
#       # easy_install requests
#
# Usage:
#
#        Usage: activeMQ.py [options]
#
#        Options:
#          -h, --help            show this help message and exit
#          -v, --verbose         verbose output
#          -H HOSTNAME, --hostname=HOSTNAME
#                                hostname EPAgent is running on
#          -p PORT, --port=PORT  port EPAgent is connected to
#          -m METRICPATH, --metric_path=METRICPATH
#                                metric path header for all metrics
#          -u USER:PASSWORD, --user=USER:PASSWORD
#                                user and password for ActiveMQ JMX access
#          -b BROKERHOSTNAME, --broker=BROKERHOSTNAME
#                                hostname of ActiveMQ broker
#          -j JMX_PORT, --jmx_port=JMX_PORT
#                                JMX port of ActiveMQ broker


import json
import optparse
#import random
import requests
#import socket
import sys
import time
import urllib2
import base64
from datetime import datetime
import ssl

def callUrl(url, username):
    if sys.version_info[:2] == (2, 6):
        # This is a workaround for users of Python 2.6
        # for Basic Authentication and ignore cert warnings
        
        # split username and password
        user,pswd = username.split(":")
        
        p = urllib2.HTTPPasswordMgrWithDefaultRealm()
        p.add_password(None, url, user, pswd)
        
        handler = urllib2.HTTPBasicAuthHandler(p)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener) 
        
        try:
            response = urllib2.urlopen(url).read()
        except urllib2.URLError as err:
            print("Unable to connect to ActiveMQ broker via URL \"{0}\": {1}\ncheck URL, port and that jolokia is enabled!".format(url, err))
            sys.exit(1)
        data = json.loads(response)
    else:
        request = urllib2.Request(url)
        # You need the replace to handle encodestring adding a trailing newline
        # (https://docs.python.org/2/library/base64.html#base64.encodestring)
        base64string = base64.encodestring('%s' % (username)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        
        # Workaround to ignore cert warnings for Python 2.7
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        
        # Workaround to ignore cert warnings also works for version Python 2.7.9+
        #ctx = ssl.create_default_context()
        #ctx.check_hostname = False
        #ctx.verify_mode = ssl.CERT_NONE
        
        try:
            response = urllib2.urlopen(request, context=ctx)
        except urllib2.URLError as err:
            print("Unable to connect to ActiveMQ broker via URL \"{0}\": {1}\ncheck URL, port and that jolokia is enabled!".format(url, err))
            sys.exit(1)
        data = json.loads(response.read())
        
    # print(json.dumps(data, sort_keys=True, indent=4))
    return data
    
    

def writeMetrics(values, metricPath, metricDict):

    for key in values.keys():
        #if (type(values[key]) is list
        #if (type(values[key]) is dict

        #print('type of {}:{} is {}'.format(key, values[key], type(values[key])))

        if (type(values[key]) is unicode):
            m = {}
            m['type'] = 'StringEvent'
            m['name'] = metricPath + ':{0}'.format(key)
            m['value']= "{0}".format(values[key])
            metricDict['metrics'].append(m)

        if (type(values[key]) is int):
            # ends with 'Limit'?
            if (-1 < key.find('Limit', len(key)-5, len(key))):
                m = {}
                m['type'] = 'LongCounter'
                m['name'] = metricPath + ':{0}'.format(key)
                m['value']= "{0}".format(values[key])
                metricDict['metrics'].append(m)
            else:
                if ((-1 < key.find('Average', 0, 7)) or (-1 < key.find('PercentUsage', len(key)-12, len(key)))):
                    # should be IntPercentage for 'PercentUsage' but this is not a EPA supported metric data type
                    m = {}
                    m['type'] = 'IntAverage'
                    m['name'] = metricPath + ':{0}'.format(key)
                    m['value']= "{0}".format(values[key])
                    metricDict['metrics'].append(m)
                else:
                    m = {}
                    m['type'] = 'IntCounter'
                    m['name'] = metricPath + ':{0}'.format(key)
                    m['value']= "{0}".format(values[key])
                    metricDict['metrics'].append(m)

        if (type(values[key]) is bool):
            if (-1 == key.find('Limit', len(key)-5, len(key))):
                m = {}
                m['type'] = 'IntAverage'
                m['name'] = metricPath + ':{0}'.format(key)
                if (values[key]):
                    m['value']= '1'
                else:
                    m['value']= '0'
                metricDict['metrics'].append(m)

        if (type(values[key]) is float):
            m = {}
            m['type'] = 'IntCounter'
            m['name'] = metricPath + ':{0}'.format(key)
            m['value']= "{0}".format(int(float(values[key] + .5)))
            metricDict['metrics'].append(m)



def collectActiveMQ(metricDict, metricPath, brokerhost, jmxport, brokername, username):

    """
    Conversion of JMX data into metrics to be harvested
    """

    url = "https://{0}:{1}/api/jolokia/read/org.apache.activemq:type=Broker,brokerName={2}".format(brokerhost, jmxport, urllib2.quote(brokername))

    data = callUrl(url, username)
        
    if (data.has_key('value')):
        values = data['value']

        brokerMetricPath = metricPath + '|Broker|' + values['BrokerName']
        #brokerMetricPath = metricPath + '|' + values['BrokerName']
        writeMetrics(values, brokerMetricPath, metricDict)

        """
        serviceUrl = url + ",Service=Health"
        data = callUrl(serviceUrl, username)
        """

        destinationTypes = ['Queues', 'Topics', 'TemporaryQueues', 'TemporaryTopics']

        for destinationType in destinationTypes:
            for destination in values[destinationType]:
                objName = destination['objectName']
                index = objName.index('destinationName=')
                start = index + len('destinationName=')
                end = objName.index(',', index)
                destName = objName[start:end]

                if (-1 == destName.find('ActiveMQ.Advisory.')):
                    # print("url=" + url)
                    # print("destinationType=" + destinationType)
                    # print("destinationType-1=" + destinationType[:-1])
                    # print("destName=" + urllib2.quote(destName))

                    destUrl = "{0},destinationType={1},destinationName={2}".format(url, destinationType[:-1], urllib2.quote(destName))
                    # print(destUrl)
                    data = callUrl(destUrl, username)
                        

                    if (data.has_key('value')):
                        destMetricPath = metricPath + '|Broker|' + values['BrokerName'] + '|' + destinationType + '|' + destName
                        writeMetrics(data['value'], destMetricPath, metricDict)

    """
    values = data['value']

    brokerMetricPath = brokerMetricPath + '|Health'
    writeMetrics(values, brokerMetricPath, metricDict)
    """



def main(argv):

    parser = optparse.OptionParser()
    parser.add_option("-v", "--verbose", help = "verbose output",
        dest = "verbose", default = False, action = "store_true")

    parser.add_option("-H", "--hostname", default = "localhost",
        help = "hostname EPAgent is running on", dest = "hostname")
    parser.add_option("-p", "--port", help = "port EPAgent is connected to",
        type = "int", default = 8080, dest = "port")
    parser.add_option("-m", "--metric_path", help = "metric path header for all metrics",
        dest = "metricPath", default = "ActiveMQ")
    parser.add_option("-u", "--user", help = "user and password for ActiveMQ JMX access",
        dest = "user", default = "admin:admin")
    parser.add_option("-b", "--broker_host", help = "hostname of ActiveMQ broker",
        dest = "brokerhost", default = "localhost")
    parser.add_option("-j", "--jmx_port", help = "JMX port of ActiveMQ broker",
        type = "int", dest = "jmxport", default = "8161")
    parser.add_option("-n", "--broker_name", help = "name of ActiveMQ broker",
        dest = "brokername", default = "localhost")

    (options, args) = parser.parse_args();

    if options.verbose == True:
        print("Verbose enabled")

    # Configure URL and header for RESTful submission
    url = "http://{0}:{1}/apm/metricFeed".format(options.hostname,
        options.port)
    headers = {'content-type': 'application/json'}

    if options.verbose:
        print("Submitting to: {0}".format(url))

    submissionCount = 0



    while True:

        start = datetime.now()

        # Metrics are collected in the metricDict dictionary.
        metricDict = {'metrics' : []}

        collectActiveMQ(metricDict, options.metricPath, options.brokerhost, options.jmxport, options.brokername, options.user)

        #
        # convert metric Dictionary into a JSON message via the
        # json package.  Post resulting message to EPAgent RESTful
        # interface.
        #
        try:
            r = requests.post(url, data = json.dumps(metricDict),
                              headers = headers)
        except requests.ConnectionError as err:
            print("Unable to connect to EPAgent via URL \"{0}\": {1}\ncheck httpServerPort and that EPAgent is running!".format(url, err))
            sys.exit(1)


        if options.verbose:
            print("jsonDump:")
            print(json.dumps(metricDict, indent = 4))

            print("Response:")
            response = json.loads(r.text)
            print(json.dumps(response, indent = 4))

            print("StatusCode: {0}".format(r.status_code))

        submissionCount += 1
        # print("Submitted metric: {0}".format(submissionCount))

        end = datetime.now()
        delta = end-start
        howlong = 15.0 - delta.seconds
        howlong = (howlong * 100000 - delta.microseconds) / 100000
        time.sleep(howlong)

if __name__ == "__main__":
    main(sys.argv)
''
