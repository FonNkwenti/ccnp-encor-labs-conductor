import sys
import os
import argparse

# Add common tools to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject_challenge_1(injector):
    """Receive-Only Stub on R5"""
    print("Injecting Challenge 1: Receive-Only Stub on R5...")
    commands = [
        "router eigrp 100",
        " eigrp stub receive-only"
    ]
    injector.execute_commands(5005, commands, "R5 Receive-Only")

def inject_challenge_2(injector):
    """Timer Mismatch on R1/R2"""
    print("Injecting Challenge 2: Timer Mismatch on R1...")
    # We change R1 to have a very short hold time while R2 remains long
    commands = [
        "interface FastEthernet1/0",
        " ip hello-interval eigrp 100 60",
        " ip hold-time eigrp 100 70"
    ]
    injector.execute_commands(5001, commands, "R1 Short Hold Timer")

def inject_challenge_3(injector):
    """Missing static keyword in stub config"""
    print("Injecting Challenge 3: Missing Static in Stub...")
    # First ensure a static route exists
    # Then ensure stub is restricted
    commands = [
        "ip route 192.168.99.0 255.255.255.0 Null0",
        "router eigrp 100",
        " redistribute static",
        " eigrp stub connected summary"
    ]
    injector.execute_commands(5005, commands, "R5 Redistribute Static but Stub restricted")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fault Injector for EIGRP Lab 04")
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