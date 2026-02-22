import sys

# ===== HEAP SORT IMPLEMENTATION ======

def heapify(arr, n, i):

    largest = i
    l = 2 * i + 1
    r = 2 * i + 2

    if l < n and arr[l] > arr[largest]:
        largest = l

    if r < n and arr[r] > arr[largest]:
        largest = r

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]

        heapify(arr, n, largest)

def heap_sort(arr):
    n = len(arr)

    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    for i in range(n - 1, 0, -1):

        arr[0], arr[i] = arr[i], arr[0]

        heapify(arr, i, 0)



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
        print("Usage: python marge_sort.py <dataset>")
        sys.exit(1)

    dataset_size = sys.argv[1]
    values = get_values_from_dataset(dataset_size)
    heap_sort(values)

if __name__ == "__main__":
    main()