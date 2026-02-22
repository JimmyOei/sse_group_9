const fs = require("fs");

function quickSort(arr) {
    if (arr.length <= 1) {
        return arr;
    }

    const pivot = arr[Math.floor(arr.length / 2)];
    const left = arr.filter(x => x < pivot);
    const middle = arr.filter(x => x === pivot);
    const right = arr.filter(x => x > pivot);

    return [...quickSort(left), ...middle, ...quickSort(right)];
}

function getValuesFromDataset(datasetName) {
    const data = fs.readFileSync("datasets/input-" + datasetName + ".txt", "utf8");
    const lines = data.split("\n");

    const numbers = [];
    for (let line of lines) {
        line = line.trim();
        if (line.length > 0) {
            numbers.push(parseInt(line, 10));
        }
    }

    return numbers;
}

function main() {
    if (process.argv.length !== 3) {
        console.log("Usage: node quick_sort.js <dataset_size>");
        process.exit(1);
    }

    const datasetName = process.argv[2];
    const values = getValuesFromDataset(datasetName);
    console.log(quickSort(values));
}

main();
