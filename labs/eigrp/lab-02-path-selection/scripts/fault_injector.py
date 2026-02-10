import sys
import os
import argparse

# Add common tools to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject_challenge_1(injector):
    """Feasibility Condition Failure
    We artificially increase the RD of R3 from the perspective of R1's backup link
    so that RD > FD of the successor.
    """
    print("Injecting Challenge 1: Feasibility Condition Failure...")
    # On R3, we increase the delay of its loopback to inflate the RD reported to R1
    commands = [
        "interface Loopback0",
        " delay 20000"
    ]
    injector.execute_commands(5003, commands, "R3 Loopback Delay (Feasibility)")

def inject_challenge_2(injector):
    """Extreme Delay on Primary Link"""
    print("Injecting Challenge 2: Primary Link Delay Inflation...")
    commands = [
        "interface FastEthernet1/0",
        " delay 100000"
    ]
    injector.execute_commands(5001, commands, "R1 Fa1/0 High Delay")

def inject_challenge_3(injector):
    """Offset-list to make direct link unattractive"""
    print("Injecting Challenge 3: Offset-list Metric Inflation...")
    commands = [
        "access-list 10 permit 3.3.3.3",
        "router eigrp 100",
        " offset-list 10 in 1000000 FastEthernet1/1"
    ]
    injector.execute_commands(5001, commands, "R1 Offset-list")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fault Injector for EIGRP Lab 02")
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