#!/usr/bin/env python3
"""
Demo script for Code Runner and Debugging
This script demonstrates various debugging features
"""


def calculate_sum(numbers):
    """Calculate sum of numbers with debugging demonstration"""
    total = 0
    for i, num in enumerate(numbers):
        print(f"Processing number {i+1}: {num}")
        total += num
        # Breakpoint can be set here for debugging
    return total


def divide_numbers(a, b):
    """Demonstrate error handling for debugging"""
    try:
        result = a / b
        print(f"Result: {a} / {b} = {result}")
        return result
    except ZeroDivisionError as e:
        print(f"Error: {e}")
        return None


def main():
    """Main function demonstrating Code Runner features"""
    print("🔥 Code Runner & Debug Demo")
    print("=" * 30)

    # Test calculations
    numbers = [1, 2, 3, 4, 5]
    print(f"\nCalculating sum of {numbers}")
    result = calculate_sum(numbers)
    print(f"Total sum: {result}")

    # Test division
    print("\nTesting division:")
    divide_numbers(10, 2)
    divide_numbers(10, 0)  # This will cause an error

    print("\n✅ Demo completed!")


if __name__ == "__main__":
    main()
