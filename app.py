from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- Шаблон главной страницы (с формой и результатом) ---
INDEX_PAGE = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Калькулятор матриц</title>
  <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
  <main class="card">
    <h1>Калькулятор матриц</h1>

    <form action="/" method="post" class="form">
      <label for="matrix_a">Матрица A</label>
      <textarea id="matrix_a" name="matrix_a" rows="6" placeholder="1 2 3&#10;4 5 6">{{matrix_a}}</textarea>

      <label for="matrix_b">Матрица B</label>
      <textarea id="matrix_b" name="matrix_b" rows="6" placeholder="5 6&#10;7 8">{{matrix_b}}</textarea>

      <label for="operation">Операция</label>
      <select id="operation" name="operation">
        <option value="add" {% if op=="add" %}selected{% endif %}>A + B</option>
        <option value="sub" {% if op=="sub" %}selected{% endif %}>A - B</option>
        <option value="mul" {% if op=="mul" %}selected{% endif %}>A × B</option>
        <option value="transpose" {% if op=="transpose" %}selected{% endif %}>Транспонировать A</option>
        <option value="det" {% if op=="det" %}selected{% endif %}>Определитель A</option>
        <option value="inverse" {% if op=="inverse" %}selected{% endif %}>Обратная A</option>
      </select>

      <div class="row">
        <button type="submit" class="btn">Посчитать</button>
        <button type="reset" class="btn muted">Очистить</button>
      </div>
    </form>

    {% if op %}
      <section style="margin-top:20px;">
        <h2>Результат ({{op}})</h2>
        {% if err %}
          <div style="color:#b91c1c;margin-top:10px;"><strong>Ошибка:</strong> {{err}}</div>
        {% else %}
          <pre style="margin-top:12px;">{{result_text}}</pre>
        {% endif %}
      </section>
    {% endif %}

    <section class="note">
      <strong>Формат ввода:</strong><br>
      Строки — новые строки, числа через пробел.<br>
      Пример 2×2:<br>
      <pre>1 2
3 4</pre>
    </section>

    <footer class="foot">Простой учебный проект без JavaScript</footer>
  </main>
</body>
</html>
"""

# ---------- функции работы с матрицами ----------
def parse_matrix(text):
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if not lines:
        return []
    mat = []
    row_len = None
    for i, ln in enumerate(lines):
        parts = ln.replace(',', '.').split()
        row = [float(p) for p in parts]
        if row_len is None:
            row_len = len(row)
        elif len(row) != row_len:
            raise ValueError(f"Строки разной длины (строка {i+1})")
        mat.append(row)
    return mat

def shape(m): return (len(m), len(m[0]) if m and m[0] else 0)

def add(A,B): return [[A[i][j]+B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

def sub(A,B): return [[A[i][j]-B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

def mul(A,B):
    r1,c1 = shape(A); r2,c2 = shape(B)
    if c1 != r2: raise ValueError("Столбцов A должно быть = строк B")
    return [[sum(A[i][k]*B[k][j] for k in range(c1)) for j in range(c2)] for i in range(r1)]

def transpose(A): return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]

def det(A):
    n,_ = shape(A)
    if n != shape(A)[1]: raise ValueError("Определитель только для квадратной матрицы")
    if n == 1: return A[0][0]
    if n == 2: return A[0][0]*A[1][1]-A[0][1]*A[1][0]
    res=0
    for col in range(n):
        minor=[[A[i][j] for j in range(n) if j!=col] for i in range(1,n)]
        res+=((-1)**col)*A[0][col]*det(minor)
    return res

def inverse(A):
    n,_=shape(A)
    if n!=shape(A)[1]: raise ValueError("Только квадратная матрица")
    M=[row[:] for row in A]; I=[[float(i==j) for j in range(n)] for i in range(n)]
    for i in range(n):
        pivot=M[i][i]
        if abs(pivot)<1e-12:
            for r in range(i+1,n):
                if abs(M[r][i])>1e-12:
                    M[i],M[r]=M[r],M[i]; I[i],I[r]=I[r],I[i]; pivot=M[i][i]; break
            else: raise ValueError("Матрица вырождена")
        M[i]=[v/pivot for v in M[i]]; I[i]=[v/pivot for v in I[i]]
        for r in range(n):
            if r==i: continue
            coef=M[r][i]
            M[r]=[M[r][c]-coef*M[i][c] for c in range(n)]
            I[r]=[I[r][c]-coef*I[i][c] for c in range(n)]
    return I

def mat_to_text(M):
    if isinstance(M,(int,float)): return str(round(M,6))
    return "\n".join("  ".join(f"{v:.6g}" for v in row) for row in M)

# --- маршруты ---
@app.route("/", methods=["GET","POST"])
def home():
    result_text=""; err=None; op=None
    matrix_a=""; matrix_b=""
    if request.method=="POST":
        matrix_a=request.form.get("matrix_a","")
        matrix_b=request.form.get("matrix_b","")
        op=request.form.get("operation","")
        try:
            A=parse_matrix(matrix_a) if matrix_a.strip() else []
            B=parse_matrix(matrix_b) if matrix_b.strip() else []
            if op=="add": result_text=mat_to_text(add(A,B))
            elif op=="sub": result_text=mat_to_text(sub(A,B))
            elif op=="mul": result_text=mat_to_text(mul(A,B))
            elif op=="transpose": result_text=mat_to_text(transpose(A))
            elif op=="det": result_text=str(det(A))
            elif op=="inverse": result_text=mat_to_text(inverse(A))
            else: err="Неизвестная операция"
        except Exception as e: err=str(e)
    return render_template_string(INDEX_PAGE,
        result_text=result_text, err=err, op=op,
        matrix_a=matrix_a, matrix_b=matrix_b)

if __name__=="__main__":
    app.run(debug=True)
