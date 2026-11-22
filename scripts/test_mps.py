#!/usr/bin/env python3
import sys

def main():
    print("==========================================")
    print("    APPLE SILICON / MPS TEST SCRIPT      ")
    print("==========================================")
    
    # 1. PyTorch installation check
    try:
        import torch
        print(f"PyTorch Version: {torch.__version__}")
    except ImportError as e:
        print(f"PyTorch Import Error: {e}")
        print("MPS NOT AVAILABLE")
        sys.exit(1)
        
    # 2. CPU availability
    print("CPU: AVAILABLE")
    
    # 3. MPS availability check
    mps_built = hasattr(torch.backends, "mps") and torch.backends.mps.is_built()
    mps_available = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    
    print(f"MPS Built in PyTorch: {mps_built}")
    print(f"MPS Available on OS/Hardware: {mps_available}")
    
    if not mps_available:
        print("------------------------------------------")
        print("MPS NOT AVAILABLE")
        print("------------------------------------------")
        sys.exit(0)

    # 4. Small tensor & model execution on MPS
    try:
        device = torch.device("mps")
        
        # Test tensor operations on MPS
        x = torch.randn(10, 10, device=device)
        y = torch.randn(10, 10, device=device)
        z = torch.matmul(x, y)
        
        # Test small neural network layer on MPS
        linear = torch.nn.Linear(10, 5).to(device)
        out = linear(z)
        
        # Bring tensor back to CPU to verify computation
        result_sum = out.cpu().sum().item()
        
        print(f"Tensor computation on MPS successful. Output scalar sum: {result_sum:.4f}")
        print("------------------------------------------")
        print("MPS AVAILABLE")
        print("------------------------------------------")
    except Exception as exc:
        print(f"Error executing tensor operations on MPS: {exc}")
        print("------------------------------------------")
        print("MPS NOT AVAILABLE")
        print("------------------------------------------")

if __name__ == "__main__":
    main()
