from base64 import b64decode
import os

import random
from MonsterLab import Monster
from flask import Flask, render_template, request, jsonify, send_file, Response
from pandas import DataFrame
import xgboost as xgb
import pandas as pd
from app.data import Database
from app.graph import chart
from app.machine import Machine
from app.utils import load_your_data_function, save_model, preprocess_data

SPRINT = 3
APP = Flask(__name__)


@APP.route("/")
def home():
    return render_template(
        "home.html",
        sprint=f"Sprint {SPRINT}",
        monster=Monster().to_dict(),
        password=b64decode(b"VGFuZ2VyaW5lIERyZWFt"),
    )


@APP.route("/data")
def data():
    if SPRINT < 1:
        return render_template("data.html")
    db = Database()
    return render_template(
        "data.html",
        count=db.count(),
        table=db.html_table(),
    )


@APP.route("/view", methods=["GET", "POST"])
def view():
    if SPRINT < 2:
        return render_template("view.html")
    db = Database()
    options = ["Level", "Health", "Energy", "Sanity", "Rarity"]
    x_axis = request.values.get("x_axis") or options[1]
    y_axis = request.values.get("y_axis") or options[2]
    target = request.values.get("target") or options[4]
    graph = chart(
        df=db.dataframe(),
        x=x_axis,
        y=y_axis,
        target=target,
    ).to_json()
    return render_template(
        "view.html",
        options=options,
        x_axis=x_axis,
        y_axis=y_axis,
        target=target,
        count=db.count(),
        graph=graph,
    )


@APP.route("/model", methods=["GET", "POST"])
def model():
    if SPRINT < 3:
        return render_template("model.html")
    db = Database()
    options = ["Level", "Health", "Energy", "Sanity", "Rarity"]
    filepath = os.path.join("app", "model.joblib")
    if not os.path.exists(filepath):
        df = db.dataframe()
        machine = Machine(df[options])
        machine.save(filepath)
    else:
        machine = Machine.open(filepath)
    stats = [round(random.uniform(1, 250), 2) for _ in range(3)]
    level = request.values.get("level", type=int) or random.randint(1, 20)
    health = request.values.get("health", type=float) or stats.pop()
    energy = request.values.get("energy", type=float) or stats.pop()
    sanity = request.values.get("sanity", type=float) or stats.pop()
    prediction, confidence = machine(DataFrame(
        [dict(zip(options, (level, health, energy, sanity)))]
    ))
    confidence = confidence[0] if confidence else 0.0
    info = machine.info()
    return render_template(
        "model.html",
        info=info,
        level=level,
        health=health,
        energy=energy,
        sanity=sanity,
        prediction=prediction,
        confidence=f"{confidence:.2%}",
    )


@APP.route('/reset-db', methods=['POST'])
def reset_db():
    db = Database()
    db.reset()
    db.seed(amount=100)
    return jsonify({"message": "Database reset and reseeded successfully."})


@APP.route('/retrain-model', methods=['POST'])
def retrain_model():
    df = load_your_data_function()
    df = preprocess_data(df)
    print("Columns in DataFrame after preprocessing:", df.columns)
    print("Data types in DataFrame:", df.dtypes)

    # Convert categorical columns to numeric
    for col in ['Name', 'Type']:
        if df[col].dtype == 'object' or df[col].dtype.name == 'category':
            df[col] = df[col].astype('category').cat.codes

    target_column_name = 'Rarity'
    if target_column_name not in df.columns:
        return jsonify({"error": f"Target column '{target_column_name}' missing in the data"}), 400

    df[target_column_name] = pd.to_numeric(df[target_column_name], errors='coerce')
    df[target_column_name] = df[target_column_name].fillna(0)

    X = df.drop(target_column_name, axis=1)
    y = df[target_column_name]

    # Convert data to DMatrix format
    dtrain = xgb.DMatrix(X, label=y)

    params = {'objective': 'reg:squarederror', 'eval_metric': 'rmse'}
    model = xgb.train(params, dtrain, num_boost_round=10)
    model.save_model('app/model.joblib')

    return jsonify({"message": "Model re-trained and saved successfully."})


@APP.route('/download-model', methods=['GET'], endpoint='download_model_v1')
def download_model():
    filepath = os.path.join("app", "model.blst")
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({"error": "Model file not found."}), 404


@APP.route('/download-dataset', methods=['GET'])
def download_dataset():
    df = load_your_data_function()
    csv_data = df.to_csv(index=False)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=dataset.csv"}
    )


if __name__ == '__main__':
    APP.run()
