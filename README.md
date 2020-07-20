# Programmable Flexible VXLAN Tunnels

This article shows an example of provisioning Juniper Flexible Routes/Tunnels and atributes from JET APIs using gRPC [Ubuntu Server]. 

## Requirements:
- Ubuntu Server [Python3, gRPC and other dependencies]
- JET IDL bundle
- vMX [18.2X75-D30.26] or any other Trio family based JUNOS device supporting JET

### Technical References:

  [General Python language reference](https://www.python.org/doc/) \
  [gRPC](https://grpc.io/docs/tutorials/basic/python/) \
  [Protobuf Basics for Python: Python-oriented intro to Protocol Buffers](https://developers.google.com/protocol-buffers/docs/pythontutorial) \
  [Programmable Flexible VXLAN Tunnels](https://www.juniper.net/documentation/en_US/junos/topics/concept/vxlan-programmable-flex-tunnels.html) \
  [Juniper Extension Toolkit (JET)](https://www.juniper.net/documentation/en_US/jet20.1/topics/concept/juniper-extenion-toolkit-overview.html)


### JET Setup at Ubuntu
    ** Ignore this step if you are planning to use JET IDL version (20.1): ** \ 
        Instruction to generate Python dependent modules from gRPC \
        python -m grpc_tools.protoc -I=/ProtocolBufferFileLocation/ --python_out=/YourPythonJsonScriptLocation/ --grpc_python_out=/YourPythonJsonScriptLocation /ProtocolBufferFileLocation/*.proto

    - if you plan to use different JET IDL version, download the JET IDL TAR from JUNOS download page and untar it at your location.
    - rename the folder with file *.proto to folder 'proto'
    [example] python -m grpc_tools.protoc -I=/home/vinayt/JET/proto --python_out=/home/vinayt/JET/ --grpc_python_out=/home/vinayt/JET/ /home/vinayt/JET/proto/*.proto
        - In this example my python script, JSON and gRPC modules were at /home/vinayt/JET/ and *.proto files from JET IDL were at /home/vinayt/JET/proto/
   

### Instruction to Execute Python Script on Ubuntu Server/JET API to program and delete flexible tunnels from JUNOS/vMX:
    [Example] python route_inject_p3.py -H <router fxp0 IP > -P <JET port configured at router> -U <Router UserName> -W <Router Passwd>  -F <JSON File>

      # ipv4 traffic over ipv4 tunnel
      [program] python route_inject_p3.py -H 10.49.169.105 -P 50051 -U lab -W lab123  -F encap_tunnel_profile-ipv4-vxlanv4.json
      [delete] python route_inject_p3.py -H 10.49.169.105 -P 50051 -U lab -W lab123  -F encap_tunnel_profile-ipv4-vxlanv4.json --op del

      # ipv4 traffic over ipv6 tunnel
      [program] python route_inject_p3.py -H 10.49.169.105 -P 50051 -U lab -W lab123  -F encap_tunnel_profile-ipv4-vxlanv6.json
      [delete] python route_inject_p3.py -H 10.49.169.105 -P 50051 -U lab -W lab123  -F encap_tunnel_profile-ipv4-vxlanv6.json --op del

      # ipv6 traffic over ipv6 tunnel
      [program] python route_inject_p3.py -H 10.49.169.105 -P 50051 -U lab -W lab123  -F encap_tunnel_profile-ipv6-vxlanv6.json
      [delete] python route_inject_p3.py -H 10.49.169.105 -P 50051 -U lab -W lab123  -F encap_tunnel_profile-ipv6-vxlanv6.json --op del 

      # Decapsulation Profile 
      [program] python decap_inject.py -H 10.49.169.105 -P 50051 -U lab -W lab123  -F  decap_tunnel_profile.json
      [delete] python decap_inject.py -H 10.49.169.105 -P 50051 -U lab -W lab123  -F  <<decap-delelte.json>> --op del
               => For delete, the input json file should just be a list of tunnel names, eg:
                      => { "tunnel_profile_names": [ "foo", "bar" ] }

### Junos/vMX Configuration:

    set system services extension-service request-response grpc clear-text address <fxp0/em0: 10.49.169.105>
    set system services extension-service request-response grpc clear-text port <port number: 50051>
    set system services extension-service request-response grpc skip-authentication

    set routing-options programmable-rpd purge-timeout <time|never>
    
    set interfaces fti0 unit 48 tunnel encapsulation vxlan-gpe source address 10.3.129.101
    set interfaces fti0 unit 48 tunnel encapsulation vxlan-gpe destination address 157.55.252.109
    set interfaces fti0 unit 48 tunnel encapsulation vxlan-gpe tunnel-endpoint vxlan
    set interfaces fti0 unit 48 tunnel encapsulation vxlan-gpe destination-udp-port 65330
    set interfaces fti0 unit 48 tunnel encapsulation vxlan-gpe vni 992652
    set interfaces fti0 unit 48 family inet address 10.254.3.229/27
    set interfaces fti0 unit 48 family inet6

###  IPv4 traffic over IPv4 Tunnel: 

This sample output shows the static route [40.40.40.2] entry in JUNOS device [vMX] after pushing static route and Programable IPv4 Flexible Tunnel from the Server;
 * JSON [encap_tunnel_profile-ipv4-vxlanv4.json] was used for following example
    
          regress@exr02.chg> show route 40.40.40.2 extensive    

          0113d92171084d118320eaa988f24ea0.inet.0: 7 destinations, 7 routes (7 active, 0 holddown, 0 hidden)

          40.40.40.2/32 (1 entry, 1 announced)
          TSI:
          KRT in-kernel 40.40.40.2/32 -> {fti0.48 Flags NSR-incapable}
          Opaque data client: FLEX-TNL
          Address: 0xd6ac220
          Opaque-data reference count: 2
          Opaque data: Flexible IPv4 VXLAN tunnel profile
                  *Static Preference: 5/100
                          Next hop type: Router, Next hop index: 2407
                          Address: 0xc8d1030
                          Next-hop reference count: 3
                          Next hop: via fti0.48, selected
                          Session Id: 0x142
                          State: <Active Int NSR-incapable OpaqueData Programmed>
                          Age: 10 
                          Validation State: unverified 
                          Announcement bits (2): 0-KRT 2-Resolve tree 3 
                          AS path: I 
                          Flexible IPv4 VXLAN tunnel profile
                              Action: Encapsulate
                              Interface: fti0.48 (Index: 407)
                              VNI: 992652
                              Source Prefix: 10.3.129.101/32
                              Source UDP Port Range: 49152 - 65535
                              Destination Address: 157.55.252.109
                              Destination UDP Port: 65330
                              Destination MAC Address: 1a:2b:3c:4a:5a:6a
                              VXLAN Flags: 0x08
 
 
### IPv4 traffic over IPv6 tunnel: 

This sample output shows the static route [40.1.1.1] entry in JUNOS device [vMX] after pushing static route and Programable IPv6 Flexible Tunnel from the Server; 
 * JSON [encap_tunnel_profile-ipv4-vxlanv6.json] was used for following example 

        regress@exr02.chg> show route 40.1.1.1 extensive 

        0113d92171084d118320eaa988f24ea0.inet.0: 7 destinations, 7 routes (7 active, 0 holddown, 0 hidden)

        40.1.1.1/32 (1 entry, 1 announced)
        TSI:
        KRT in-kernel 40.1.1.1/32 -> {fti0.48 Flags NSR-incapable}
        Opaque data client: FLEX-TNL
        Address: 0xd6ac220
        Opaque-data reference count: 2
        Opaque data: Flexible IPv6 VXLAN tunnel profile
                *Static Preference: 5/100
                        Next hop type: Router, Next hop index: 2407
                        Address: 0xc8d10f0
                        Next-hop reference count: 3
                        Next hop: via fti0.48, selected
                        Session Id: 0x142
                        State: <Active Int NSR-incapable OpaqueData Programmed>
                        Age: 18 
                        Validation State: unverified 
                        Announcement bits (2): 0-KRT 2-Resolve tree 3 
                        AS path: I 
                        Flexible IPv6 VXLAN tunnel profile
                            Action: Encapsulate
                            Interface: fti0.48 (Index: 407)
                            VNI: 2
                            Source Prefix: abcd::20:0:0:2/128
                            Source UDP Port Range: 49152 - 65535
                            Destination Address: abcd::20:0:0:1
                            Destination UDP Port: 4789
                            VXLAN Flags: 0x08


### IPv6 traffic over IPv6 tunnel: 

This sample output shows the static route [abcd::40:1:1:1] entry JUNOS device [vMX] after pushing static route and Programable IPv6 Flexible Tunnel from the Server; 
  * JSON [encap_tunnel_profile-ipv6-vxlanv6.json] was used for following example 

          regress@exr02.chg> show route abcd::40:1:1:1 extensive 

          0113d92171084d118320eaa988f24ea0.inet6.0: 3 destinations, 3 routes (3 active, 0 holddown, 0 hidden)
          abcd::40:1:1:1/128 (1 entry, 1 announced)
          TSI:
          KRT in-kernel abcd::40:1:1:1/128 -> {fti0.48 Flags NSR-incapable}
          Opaque data client: FLEX-TNL
          Address: 0xd6ac220
          Opaque-data reference count: 2
          Opaque data: Flexible IPv6 VXLAN tunnel profile
                  *Static Preference: 5/100
                          Next hop type: Router, Next hop index: 2408
                          Address: 0xc8d2170
                          Next-hop reference count: 3
                          Next hop: via fti0.48, selected
                          Session Id: 0x142
                          State: <Active Int NSR-incapable OpaqueData Programmed>
                          Age: 15 
                          Validation State: unverified 
                          Announcement bits (1): 0-KRT 
                          AS path: I 
                          Flexible IPv6 VXLAN tunnel profile
                              Action: Encapsulate
                              Interface: fti0.48 (Index: 407)
                              VNI: 2
                              Source Prefix: abcd::20:0:0:2/128
                              Source UDP Port Range: 49152 - 65535
                              Destination Address: abcd::20:0:0:1
                              Destination UDP Port: 4789
                              VXLAN Flags: 0x08
                              
 ### Tunnel Decapsulation Profile
 
 This profile is used to decapsulate the VXLAN traffic. This output shows the Decapsulation tunnel profile in effect. 
 JSON [decap_tunnel_profile.json] was used for for the example.
 
           regress@exr02.chg> show flexible-tunnels profiles detail 
          ebgp_cust_rt_fti0_48
            Client ID: app1, Route Prefix: 1.0.0.0/32, Table: __flexible_tunnel_profiles__.inet.0
            Flexible IPv4 VXLAN tunnel profile
                Action: Decapsulate
                Interface: fti0.48 (Index: 407)
                VNI: 992652
                Source Prefix: 10.3.129.101/32
                Source UDP Port Range: 49152 - 65535
                Destination Address: 157.55.252.109
                Destination UDP Port: 65330
                Destination MAC Address: 1a:2b:3c:4d:5e:6f
                VXLAN Flags: 0x08

          regress@exr02.chg> show route table __flexible_tunnel_profiles__.inet.0 extensive 

          __flexible_tunnel_profiles__.inet.0: 1 destinations, 1 routes (1 active, 0 holddown, 0 hidden)
          1.0.0.0/32 (1 entry, 1 announced)
          TSI:
          KRT in-kernel 1.0.0.0/32 -> {fti0.48 Flags NSR-incapable}
          Opaque data client: FLEX-TNL
          Address: 0xd6ac220
          Opaque-data reference count: 2
          Opaque data: Flexible IPv4 VXLAN tunnel profile
                  *Static Preference: 5/100
                          Next hop type: Router, Next hop index: 2407
                          Address: 0xc8d1090
                          Next-hop reference count: 4
                          Next hop: via fti0.48, selected
                          Session Id: 0x142
                          State: <Active Int NSR-incapable OpaqueData Programmed>
                          Age: 12:23 
                          Validation State: unverified 
                          Announcement bits (1): 0-KRT 
                          AS path: I 
                          Flexible IPv4 VXLAN tunnel profile
                              Action: Decapsulate
                              Interface: fti0.48 (Index: 407)
                              VNI: 992652
                              Source Prefix: 10.3.129.101/32
                              Source UDP Port Range: 49152 - 65535
                              Destination Address: 157.55.252.109
                              Destination UDP Port: 65330
                              Destination MAC Address: 1a:2b:3c:4d:5e:6f
                              VXLAN Flags: 0x08
