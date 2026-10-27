
from flask import Flask, request, redirect, url_for, render_template_string, jsonify
from datetime import date

app = Flask(__name__)

DAILY_TARGET = 2000
food_logs = []

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CalorieTrack | Nutrition Dashboard</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f4f7fb;
    color: #182230;
}
header {
    background: #172b4d;
    color: white;
    padding: 22px 7%;
}
header h1 { margin: 0 0 6px; font-size: 27px; }
header p { margin: 0; color: #d5dfef; }
main { max-width: 1100px; margin: 30px auto; padding: 0 18px; }
.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 16px;
}
.card, .panel {
    background: white;
    padding: 22px;
    border-radius: 14px;
    box-shadow: 0 3px 14px #14213d0c;
}
.card p { color: #65748b; margin: 0 0 12px; }
.number { font-size: 30px; font-weight: bold; }
.unit { font-size: 13px; color: #65748b; }
.progress {
    height: 12px;
    border-radius: 8px;
    background: #e6ebf2;
    overflow: hidden;
    margin-top: 14px;
}
.bar { height: 100%; background: #19a974; }
.content {
    display: grid;
    grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
    gap: 18px;
    margin-top: 22px;
}
h2 { font-size: 19px; margin-top: 0; }
label { display: block; margin: 13px 0 6px; font-size: 14px; }
input, select {
    width: 100%; padding: 11px; border: 1px solid #d6deea;
    border-radius: 8px; font-size: 14px;
}
button {
    border: 0; padding: 12px 16px; border-radius: 8px;
    background: #176b51; color: white; font-weight: bold;
    cursor: pointer; margin-top: 16px;
}
button:hover { background: #10513d; }
.reset { background: #a83243; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { padding: 11px 6px; text-align: left; border-bottom: 1px solid #edf0f5; }
th { color: #65748b; }
.notice { color: #65748b; font-size: 13px; line-height: 1.5; }
footer { text-align: center; color: #65748b; padding: 25px; font-size: 13px; }
@media(max-width: 700px) {
    .content { grid-template-columns: 1fr; }
    main { margin-top: 18px; }
}
</style>
</head>
<body>
<header>
    <h1>CalorieTrack</h1>
    <p>Your daily nutrition and calorie dashboard</p>
</header>
<main>
    <p class="notice">Daily overview &nbsp;|&nbsp; {{ today }}</p>
    <section class="cards">
        <div class="card">
            <p>Calories Consumed</p>
            <div class="number">{{ calories }}</div>
            <span class="unit">kcal today</span>
        </div>
        <div class="card">
            <p>Calories Remaining</p>
            <div class="number">{{ remaining }}</div>
            <span class="unit">kcal to daily target</span>
        </div>
        <div class="card">
            <p>Protein</p>
            <div class="number">{{ protein }}<span class="unit"> g</span></div>
            <span class="unit">Total logged</span>
        </div>
        <div class="card">
            <p>Daily Goal</p>
            <div class="number">{{ target }}</div>
            <span class="unit">kcal target</span>
            <div class="progress">
                <div class="bar" style="width: {{ progress }}%"></div>
            </div>
            <p class="unit">{{ progress }}% of target</p>
        </div>
    </section>

    <section class="content">
        <div class="panel">
            <h2>Log a food item</h2>
            <form action="/add" method="post">
                <label>Food name</label>
                <input name="name" placeholder="e.g. Oatmeal" maxlength="60" required>

                <label>Meal</label>
                <select name="meal">
                    <option>Breakfast</option>
                    <option>Lunch</option>
                    <option>Snack</option>
                    <option>Dinner</option>
                </select>

                <label>Calories (kcal)</label>
                <input type="number" name="calories" min="0" max="10000" required>

                <label>Protein (g)</label>
                <input type="number" name="protein" min="0" max="1000" step="0.1" value="0" required>

                <label>Carbohydrates (g)</label>
                <input type="number" name="carbs" min="0" max="1000" step="0.1" value="0" required>

                <label>Fat (g)</label>
                <input type="number" name="fat" min="0" max="1000" step="0.1" value="0" required>

                <button type="submit">+ Add Food</button>
            </form>
            <form action="/reset" method="post"
                  onsubmit="return confirm('Clear all logged food entries?')">
                <button class="reset" type="submit">Reset Today's Log</button>
            </form>
        </div>

        <div class="panel">
            <h2>Today's Food Log</h2>
            {% if foods %}
            <table>
                <thead>
                    <tr><th>Food / Meal</th><th>Calories</th></tr>
                </thead>
                <tbody>
                {% for food in foods %}
                    <tr>
                        <td><strong>{{ food.name }}</strong><br>
                            <span class="unit">{{ food.meal }}</span></td>
                        <td>{{ food.calories }} kcal<br>
                            <span class="unit">P {{ food.protein }}g ·
                            C {{ food.carbs }}g · F {{ food.fat }}g</span></td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="notice">No food logged yet. Add your first meal to see your nutrition summary.</p>
            {% endif %}
            <h2 style="margin-top:24px">Macronutrients</h2>
            <p>Protein: <strong>{{ protein }} g</strong></p>
            <p>Carbohydrates: <strong>{{ carbs }} g</strong></p>
            <p>Fat: <strong>{{ fat }} g</strong></p>
            <p class="notice">Enter nutrition values from food labels or a reliable nutrition database. Values are estimates and this demo is not medical advice.</p>
        </div>
    </section>
</main>
<footer>CalorieTrack · Flask Web Application · ML DevOps ISE-2</footer>
</body>
</html>
"""

@app.route("/")
def home():
    calories = sum(item["calories"] for item in food_logs)
    protein = round(sum(item["protein"] for item in food_logs), 1)
    carbs = round(sum(item["carbs"] for item in food_logs), 1)
    fat = round(sum(item["fat"] for item in food_logs), 1)
    remaining = max(DAILY_TARGET - calories, 0)
    progress = min(round(calories / DAILY_TARGET * 100), 100)

    return render_template_string(
        HTML,
        foods=food_logs,
        calories=calories,
        remaining=remaining,
        protein=protein,
        carbs=carbs,
        fat=fat,
        target=DAILY_TARGET,
        progress=progress,
        today=date.today().strftime("%d %B %Y")
    )

@app.route("/add", methods=["POST"])
def add_food():
    name = request.form.get("name", "").strip()
    meal = request.form.get("meal", "Snack")
    allowed_meals = {"Breakfast", "Lunch", "Snack", "Dinner"}

    try:
        calories = int(request.form["calories"])
        protein = float(request.form.get("protein", 0))
        carbs = float(request.form.get("carbs", 0))
        fat = float(request.form.get("fat", 0))

        if not name or len(name) > 60:
            return "Enter a valid food name", 400
        if meal not in allowed_meals:
            return "Invalid meal selection", 400
        if not 0 <= calories <= 10000:
            return "Calories must be between 0 and 10000", 400
        if any(not 0 <= value <= 1000
               for value in (protein, carbs, fat)):
            return "Macronutrients must be between 0 and 1000 g", 400

        food_logs.append({
            "name": name,
            "meal": meal,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        })
        return redirect(url_for("home"))

    except (ValueError, KeyError):
        return "Please enter valid nutrition values", 400

@app.route("/reset", methods=["POST"])
def reset():
    food_logs.clear()
    return redirect(url_for("home"))

@app.route("/health")
def health():
    return jsonify(status="healthy", application="CalorieTrack"), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
