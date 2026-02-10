import sys
import os
import argparse

# Add common tools to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject_challenge_1(injector):
    """Local Summary Blackhole on R1"""
    print("Injecting Challenge 1: Local Summary Blackhole on R1...")
    commands = [
        "interface FastEthernet1/0",
        " ip summary-address eigrp 100 172.16.0.0 255.255.0.0"
    ]
    injector.execute_commands(5001, commands, "R1 Local Summary (Blackhole)")

def inject_challenge_2(injector):
    """Summary AD Sabotage on R3"""
    print("Injecting Challenge 2: Summary AD Sabotage on R3...")
    commands = [
        "interface FastEthernet0/0",
        " ip summary-address eigrp 100 192.168.0.0 255.255.0.0 255"
    ]
    injector.execute_commands(5003, commands, "R3 Summary AD 255")

def inject_challenge_3(injector):
    """Overly Aggressive Boundary on R7"""
    print("Injecting Challenge 3: Overly Aggressive Summary on R7...")
    commands = [
        "interface FastEthernet0/0",
        " no ip summary-address eigrp 100 172.16.0.0 255.255.0.0",
        " ip summary-address eigrp 100 0.0.0.0 0.0.0.0"
    ]
    injector.execute_commands(5007, commands, "R7 Default Route Summary")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fault Injector for EIGRP Lab 03")
    parser.add_argument("challenge", type=int, choices=[1, 2, 3], help="Challenge number to inject")
    args = parser.parse_args()

    injector = FaultInjector()
    
    if args.challenge == 1:
        inject_challenge_1(injector)
    elif args.challenge == 2:
        inject_challenge_2(injector)
    elif args.challenge == 3:
        inject_challenge_3(injector)
    
    print(f"\nChallenge {args.challenge} injected successfully.")