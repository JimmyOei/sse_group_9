import sys

def quick_sort(arr):
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]

    return quick_sort(left) + middle + quick_sort(right)

def get_values_from_dataset(dataset_size):
    numbers = []
    with open(f"datasets/input-{dataset_size}.txt", "r") as file:
        for line in file:
            line = line.strip()
            if line:
                numbers.append(int(line))
    return numbers

def main():
    if len(sys.argv) != 2:
        print("Usage: python quick_sort.py <dataset>")
        sys.exit(1)

    dataset_size = sys.argv[1]
    values = get_values_from_dataset(dataset_size)
    print(quick_sort(values))

if __name__ == "__main__":
    main()
