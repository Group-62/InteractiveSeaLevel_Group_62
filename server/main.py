from flask import Flask, render_template, redirect, request

app = Flask(__name__)

year = 0
location = ""
zoom = 0

@app.route("/", methods = ['GET','POST'])
def index():

    #if request.method == 'POST':
    #if request.form.get('button') == 'VALUE':
     #   year = request.form.get('year', -1)
      #  redirect("/world/" + year)
       # location = request.form.get('location', "")
        #redirect()
            #pass

    #elif request.method == 'GET':
     #   return render_template("index.html")

    return render_template("index.html")


@app.route("/home")
def red_home():
    return redirect('/')

@app.route("/submit", methods = ["POST"])
def submit():

    year = request.form["year"]
    location = request.form["location"]
    zoom = request.form["zoom-level"]
    return redirect("/world/" + year + "/" + location + "/" + zoom)

@app.route("/world/<int:VisYear>/<string:VisLocation>/<int:ZoomLvl>")
def see_world(VisYear, VisLocation, ZoomLvl):

    import world

    world.startVisualizationFull(ZoomLvl - 1, VisYear, VisLocation)

    return render_template("figure.html")

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port = 5000)
