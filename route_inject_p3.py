#!/usr/bin/python3.7

import time, sys, glob
import os, random
import optparse
import netaddr
import socket
import grpc

from google.protobuf import json_format as jsonf

import authentication_service_pb2 as auth_svc
import authentication_service_pb2_grpc
import rib_service_pb2 as rib_svc
import rib_service_pb2_grpc
import flexible_tunnel_profile_pb2 as flex_tnl
import prpd_common_pb2 as prpd
import jnx_addr_pb2 as jnx_addr

TIMEOUT = 60
BATCH_SIZE = 1000


parser = optparse.OptionParser()
parser.add_option('-O', '--op', action="store", dest="OPER", 
                  help="Operation (add or del)", default="add")
parser.add_option('-H', '--host', action="store", dest="HOST", 
                  help="Server host address", default="localhost")
parser.add_option('-P', '--port', action="store", dest="PORT", 
                  help="Server GRPC port", default="50051")
parser.add_option('-U', '--user', action="store", dest="USER", 
                  help="JET username", default="user")
parser.add_option('-W', '--password', action="store", dest="PASSWORD", 
                  help="JET password", default="password")
parser.add_option('-C', '--client', action="store", dest="CLIENT_ID", 
                  help="JET client ID", default="app1")
parser.add_option('-F', '--file', action="store", dest="FILE", 
                  help="JSON input file", default="config.json")
(options, args) = parser.parse_args()

if os.path.isfile(options.FILE) == False:
    print ("ERROR: Input file %s does not exist" % options.FILE)
    sys.exit(1)


def add_routes(rib, routes_req):
    print ('Adding routes....')
    i = 0
    routes_added = 0
    routes_processed = 0
    start_time = time.time()
    while len(routes_req.routes):
        this_req = rib_svc.RouteUpdateRequest(
            routes=routes_req.routes[:BATCH_SIZE])
        opRes = rib.RouteAdd(this_req, TIMEOUT)
        if opRes.status:
            print ('Batch %d: routes added = %d, result = %d'% (
                i, opRes.operations_completed, opRes.status))
        routes_added += opRes.operations_completed
        routes_processed += len(routes_req.routes[:BATCH_SIZE])
        i += 1
        del routes_req.routes[:BATCH_SIZE]
    end_time = time.time()
    print ('DONE: total of', routes_processed, 'routes processed', routes_added, 'routes added')
    print ('Elapsed time: %.2f secs' % (end_time - start_time))
    raw_input("Press the <ENTER> key to disconnect...")





def del_routes(rib, routes_req):
    print ('Deleting routes....')
    i = 0
    routes_removed = 0
    routes_processed = 0
    start_time = time.time()
    while len(routes_req.routes):
        this_req = rib_svc.RouteRemoveRequest(keys = [])
        for j in xrange(min(len(routes_req.routes), BATCH_SIZE)):
            this_req.keys.extend([routes_req.routes[j].key])
        opRes = rib.RouteRemove(this_req, TIMEOUT)
        if opRes.status:
            print ('Batch %d: routes removed = %d, result = %d'% (
                i, opRes.operations_completed, opRes.status))
        routes_removed += opRes.operations_completed
        routes_processed += len(routes_req.routes[:BATCH_SIZE])
        i += 1
        del routes_req.routes[:BATCH_SIZE]
    end_time = time.time()
    print ('DONE: total of', routes_processed, 'routes processed', routes_removed, 'routes removed')
    print ('Elapsed time: %.2f secs' % (end_time - start_time))

def Main():

    # Connect and Authenticate
    conn = grpc.insecure_channel('%s:%d' % (options.HOST, int(options.PORT)))
    auth_stub = authentication_service_pb2_grpc.LoginStub(conn)
    login = auth_stub.LoginCheck(
            auth_svc.LoginRequest(user_name=options.USER,
                                  password=options.PASSWORD,
                                  client_id=options.CLIENT_ID), 
            TIMEOUT)
    if login:
        print ("Successfully connected to server %s:%s as %s" % (
            options.HOST, options.PORT, options.USER))
    else:
        print ("ERROR: Login to server server %s:%s as %s FAILED" % (
            options.HOST, options.b, routes_req))
        sys.exit(1)

    # Create the RIB service stub
    rib = rib_service_pb2_grpc.RibStub(conn)

    # Read routes
    print ('Reading JSON input file...')
    f = open(options.FILE, "rb")
    routes_req = jsonf.Parse(f.read(), rib_svc.RouteUpdateRequest())
    print (routes_req)

    # Do stuff
    if options.OPER == 'add':
            add_routes(rib, routes_req)
    elif options.OPER == 'del':
            del_routes(rib, routes_req)
    else:
            print ('Invalid operation')

if __name__ == '__main__':
    Main()
