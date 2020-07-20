#!/usr/bin/python
#
# Copyright (c) 2018 Juniper Networks, Inc.
# All rights reserved.
#

import time, sys, glob
import os, random
import optparse
import netaddr
import socket
import grpc

from google.protobuf import json_format as jsonf

import authentication_service_pb2 as auth_svc
import authentication_service_pb2_grpc
import flexible_tunnel_service_pb2 as ft_svc
import flexible_tunnel_service_pb2_grpc
import flexible_tunnel_profile_pb2 as flex_tnl
import prpd_common_pb2 as prpd
import jnx_addr_pb2 as jnx_addr

TIMEOUT = 60
BATCH_SIZE = 1000

#
# Command line options parsing
#
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
        print "ERROR: Input file %s does not exist" % options.FILE
        sys.exit(1)

def show_sample():
    this_req = ft_svc.FlexibleTunnelDeleteRequest()
    this_req.tunnel_profile_names.append("foo")
    this_req.tunnel_profile_names.append("bar")
    print 'PROTO:'
    print this_req
    print 'JSON:'
    print jsonf.MessageToJson(this_req)

def add_profiles(ft, ft_req):
    if options.OPER == 'add':
            print 'Adding tunnels....'
    else:
            print 'Updating tunnels....'
    i = 0
    routes_added = 0
    routes_processed = 0
    start_time = time.time()
    while len(ft_req.tunnel_profiles):
        if options.OPER == 'add':
                this_req = ft_svc.FlexibleTunnelAddRequest(
                        tunnel_profiles=ft_req.tunnel_profiles[:BATCH_SIZE])
                opRes = ft.FlexibleTunnelAdd(this_req, TIMEOUT)
        else:
                this_req = ft_svc.FlexibleTunnelUpdateRequest(
                        tunnel_profiles=ft_req.tunnel_profiles[:BATCH_SIZE])
                opRes = ft.FlexibleTunnelUpdate(this_req, TIMEOUT)
        #print this_req
        #print opRes
	if opRes.code:
		print 'Batch %d: tunnels added/updated = %d, result = %d'% (
			i, opRes.operations_completed, opRes.code)
        if opRes.sub_code:
                print 'Error %d: %s' % (opRes.sub_code, opRes.message)
        routes_added += opRes.operations_completed
        routes_processed += len(ft_req.tunnel_profiles[:BATCH_SIZE])
        i += 1
        del ft_req.tunnel_profiles[:BATCH_SIZE]
    end_time = time.time()
    print 'DONE: total of', routes_processed, 'tunnels processed', routes_added, 'tunnels added/updated'
    print 'Elapsed time: %.2f secs' % (end_time - start_time)
    raw_input("Press the <ENTER> key to disconnect...")
   
def del_profiles(ft, ft_req):
    print 'Deleting tunnels....'
    i = 0
    routes_deleted = 0
    routes_processed = 0
    while len(ft_req.tunnel_profile_names):
        this_req = ft_svc.FlexibleTunnelDeleteRequest(
            tunnel_profile_names=ft_req.tunnel_profile_names[:BATCH_SIZE])
        #print this_req
        opRes = ft.FlexibleTunnelDelete(this_req, TIMEOUT)
        #print opRes
	if opRes.code:
		print 'Batch %d: tunnels added = %d, result = %d'% (
			i, opRes.operations_completed, opRes.code)
        if opRes.sub_code:
                print 'Error %d: %s' % (opRes.sub_code, opRes.message)
        routes_deleted += opRes.operations_completed
        routes_processed += len(ft_req.tunnel_profile_names[:BATCH_SIZE])
        i += 1
        del ft_req.tunnel_profile_names[:BATCH_SIZE]
    print 'DONE: total of', routes_processed, 'tunnels processed', routes_deleted, 'tunnels deleted'
    raw_input("Press the <ENTER> key to disconnect...")
   
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
        print "Successfully connected to server %s:%s as %s" % (
            options.HOST, options.PORT, options.USER)
    else:
        print "ERROR: Login to server server %s:%s as %s FAILED" % (
            options.HOST, options.PORT, options.USER)
        sys.exit(1)

    # Create the RIB service stub
    ft = flexible_tunnel_service_pb2_grpc.FlexibleTunnelStub(conn)

    # Read routes
    print 'Reading JSON input file...'
    f = open(options.FILE, "rb")

    # Do stuff
    if options.OPER == 'add':
            ft_req = jsonf.Parse(f.read(), ft_svc.FlexibleTunnelAddRequest())
            add_profiles(ft, ft_req)
    elif options.OPER == 'upd':
            ft_req = jsonf.Parse(f.read(), ft_svc.FlexibleTunnelUpdateRequest())
            add_profiles(ft, ft_req)
    elif options.OPER == 'del':
            ft_req = jsonf.Parse(f.read(), ft_svc.FlexibleTunnelDeleteRequest())
            del_profiles(ft, ft_req)
    elif options.OPER == 'sample':
            show_sample()

if __name__ == '__main__':
    Main()

