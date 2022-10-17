from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import psycopg2.extras
import requests

headers = {
	"X-RapidAPI-Key": "38521232cfmsh45424236a1926a8p1e7dc6jsnf891570cb8e9",
	"X-RapidAPI-Host": "spec-it.p.rapidapi.com"
}

app = Flask(__name__)
app.secret_key = "bkvdsfkbvsfudbhsdfbhuo"

conn = psycopg2.connect(database="PyProject_db", user="postgres", password="123", host="127.0.0.1", port="5432")


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == 'POST':
        game = request.form["gname"]
        specs = request.form["specs"]
        return redirect(url_for("game", game=game, specs=specs))
    else:
        return render_template('index.html')


@app.route('/Error')
def error():
    return render_template('Error.html')


@app.route("/Game", methods=["POST", "GET"])
def game():
    gameid = request.args.get('game')
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.args.get('specs') == "recommended":
        cur.execute("SELECT G_NAME, CPU, RAM, GPU, DX, OS, Store FROM Recommended WHERE G_NAME = %s", (gameid,))
        data = cur.fetchall()
    else:
        cur.execute("SELECT G_NAME, CPU, RAM, GPU, DX, OS, Store FROM minimal WHERE G_NAME = %s", (gameid,))
        data = cur.fetchall()
    if len(data):
        return render_template('Game.html', Game=data[0])
    else:
        url = "https://spec-it.p.rapidapi.com/"+gameid.replace(" ","-")

        response = requests.request("GET", url, headers=headers)
        #
        # if response.json()["error"] == "Error 404 | System Requirements":
        #     return redirect(url_for("error"))
        #
        # else:
        cur.execute("INSERT INTO Recommended (G_NAME, CPU, RAM, GPU, DX, OS, Store) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (gameid, response.json()["recommended"]["CPU:"], response.json()["recommended"]["RAM:"], response.json()["recommended"]["GPU:"],
                     response.json()["recommended"]["DX:"], response.json()["recommended"]["OS:"], response.json()["recommended"]["STO:"]))
        cur.execute("INSERT INTO minimal (G_NAME, CPU, RAM, GPU, DX, OS, Store) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (gameid, response.json()["minimum"]["CPU:"], response.json()["minimum"]["RAM:"], response.json()["minimum"]["GPU:"],
                     response.json()["minimum"]["DX:"], response.json()["minimum"]["OS:"], response.json()["minimum"]["STO:"]))
        conn.commit()
        if request.args.get('specs') == "recommended":
            cur.execute("SELECT G_NAME, CPU, RAM, GPU, DX, OS, Store FROM Recommended WHERE G_NAME = %s", (gameid,))
            data = cur.fetchall()
            cur.close()
        else:
            cur.execute("SELECT G_NAME, CPU, RAM, GPU, DX, OS, Store FROM minimal WHERE G_NAME = %s", (gameid,))
            data = cur.fetchall()
            cur.close()
        return render_template('Game.html', Game=data[0])


if __name__ == "__main__":
    app.run(debug=True)
