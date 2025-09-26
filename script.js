function parseMatrix(text) {
    return text.trim().split('\n').map(row => row.trim().split(/\s+/).map(Number));
}

function displayResult(result) {
    document.getElementById('result').textContent = typeof result === 'string' ? result : result.map(row => row.join(' ')).join('\n');
}

function addMatrices() {
    const A = parseMatrix(document.getElementById('matrixA').value);
    const B = parseMatrix(document.getElementById('matrixB').value);

    if (A.length !== B.length || A[0].length !== B[0].length) {
        displayResult("Ошибка: матрицы должны быть одинакового размера.");
        return;
    }

    const result = A.map((row, i) => row.map((val, j) => val + B[i][j]));
    displayResult(result);
}

function multiplyMatrices() {
    const A = parseMatrix(document.getElementById('matrixA').value);
    const B = parseMatrix(document.getElementById('matrixB').value);

    if (A[0].length !== B.length) {
        displayResult("Ошибка: число столбцов матрицы A должно совпадать с числом строк матрицы B.");
        return;
    }

    const result = Array.from({length: A.length}, () => Array(B[0].length).fill(0));

    for (let i = 0; i < A.length; i++) {
        for (let j = 0; j < B[0].length; j++) {
            for (let k = 0; k < B.length; k++) {
                result[i][j] += A[i][k] * B[k][j];
            }
        }
    }

    displayResult(result);
}

function multiplyByScalar(matrixName) {
    const M = parseMatrix(document.getElementById('matrix' + matrixName).value);
    const scalar = Number(document.getElementById('scalar').value);
    if (isNaN(scalar)) {
        displayResult("Ошибка: введите число для умножения.");
        return;
    }
    const result = M.map(row => row.map(val => val * scalar));
    displayResult(result);
}

function transposeMatrix(matrixName) {
    const M = parseMatrix(document.getElementById('matrix' + matrixName).value);
    const result = M[0].map((_, colIndex) => M.map(row => row[colIndex]));
    displayResult(result);
}

function determinantMatrix(matrixName) {
    const M = parseMatrix(document.getElementById('matrix' + matrixName).value);

    if (M.length !== M[0].length) {
        displayResult("Ошибка: детерминант можно вычислить только для квадратной матрицы.");
        return;
    }

    const det = determinant(M);
    displayResult("Детерминант: " + det);
}

function minorMatrix(matrixName) {
    const M = parseMatrix(document.getElementById('matrix' + matrixName).value);
    if (M.length < 2 || M[0].length < 2) {
        displayResult("Ошибка: минор можно вычислить только для матрицы размером хотя бы 2x2.");
        return;
    }

    // Минор элемента (1,1) - верхний левый
    const subMatrix = M.slice(1).map(row => row.slice(1));
    const det = determinant(subMatrix);
    displayResult("Минор элемента (1,1): " + det);
}

// Рекурсивная функция для вычисления детерминанта
function determinant(matrix) {
    const n = matrix.length;
    if (n === 1) return matrix[0][0];
    if (n === 2) return matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0];

    let det = 0;
    for (let i = 0; i < n; i++) {
        const subMatrix = matrix.slice(1).map(row => row.filter((_, j) => j !== i));
        det += ((i % 2 === 0 ? 1 : -1) * matrix[0][i] * determinant(subMatrix));
    }
    return det;
}
