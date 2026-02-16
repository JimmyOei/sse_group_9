import sys


# ===== MERGE SORT IMPLEMENTATION ======

def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]

    sorted_left = merge_sort(left_half)
    sorted_right = merge_sort(right_half)

    return merge(sorted_left, sorted_right)


def merge(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])

    return result




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
    print(merge_sort(values))

if __name__ == "__main__":
    main()
