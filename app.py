from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

training_data = pd.read_csv("SaltData.csv")

def get_imageJ_location():
    with open("imageJ.txt") as file:
     path = file.readline()
    file.close()
    return path

def update_imageJ_location(path):
    file = open("imageJ.txt",'w')
    path = path.replace("\\","/")
    file.write(path)
    file.close

def fix_macro(file_name):
    first_line = f'open("{os.getcwd()}/static/uploads/{file_name}");'
    modified_line = first_line.replace("\\","/")

    with open('Macro.ijm', 'r') as macro_file:
        lines = macro_file.readlines()
    lines[0] = modified_line + '\n'
    with open('NewMacro.ijm','w') as macro_file:
        macro_file.writelines(lines)

def get_measurements(file_name):
    fix_macro(file_name)
    os.system(f'java -jar "{get_imageJ_location()}" -macro "{os.getcwd()}/NewMacro.ijm"')



def train_and_pred(training_data, pred_data):
    x = training_data[["Area","Mean","StdDev","Mode","Min","Max","XM","YM",	"IntDen","Median","Skew","Kurt","RawIntDen"]]
    y = training_data['Crystal_type']
    x_to_pred = pred_data[["Area","Mean","StdDev","Mode","Min","Max","XM","YM",	"IntDen","Median","Skew","Kurt","RawIntDen"]]
    #x_train, x_test, y_train, y_test = train_test_split(x,y, test_size = 0.2, random_state = 42)
    #choosing RandomForestClassifier as decision-tree based algorithm
    clf = RandomForestClassifier(n_estimators=100, random_state = 42)
    #Training the data
    # clf.fit(x_train, y_train)

    # accuracy = accuracy_score(y_test, y_pred)
    # conf_matrix = confusion_matrix(y_test, y_pred)
    # report = classification_report(y_test, y_pred)

    # print(f"Accuracy: {accuracy * 100:.2f}%")
    # print("Confusion Matrix:")
    # print(conf_matrix)
    # print("Classification Report:")
    # print(report)


    clf.fit(x, y)
    y_predicted = clf.predict(x_to_pred)
    return (y_predicted)

@app.route('/analyze', methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect('/analyze')
        else:
            image = request.files['image']
            if image.filename == '':
                return redirect('/analyze')
            else:
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
                file_name = image.filename
                get_measurements(file_name)
                pred_data = pd.read_csv("ImageJResults.csv")
                results = train_and_pred(training_data, pred_data)
                print(results)
                return render_template('result.html',name = file_name , results=results)

    
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', images=images)

@app.route('/',methods = ['GET','POST'])
def setup():
    if request.method == 'POST':
        path = request.form["ij_path"]
        stripped_path = path.strip('"')
        if len(path) == 0:
            return redirect('/setup')
        else:
            if not os.path.isfile(stripped_path):
                return render_template('setup.html',error="File not found")
            else:
                update_imageJ_location(request.form["ij_path"])
                return redirect('/analyze')
    return render_template('setup.html',error=None)

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
