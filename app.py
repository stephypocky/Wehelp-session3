from mysql.connector import errors
from mysql.connector import pooling
from flask import *
import mysql.connector
import uuid
import base64
import boto3
import io
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

dbconfig = {
    "user":  os.getenv("user"),
    "password": os.getenv("password"),
    "host": os.getenv("host"),
    "database": os.getenv("database")
}
connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool",
                                                              pool_size=10,
                                                              pool_reset_session=True,
                                                              **dbconfig)


client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key")
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/uploadData", methods=["POST"])
def uploadData():
    comment = request.json["comment"]
    image = request.json["image"]

    # 得到的 image 是 string，必須轉換成 base64

    image_data = image.split(",")[1]
    image_data_bytes = image_data.encode()
    image_final = base64.b64decode(image_data_bytes)

    image_header = image.split(",")[0]
    image_header_final = image_header.split(":")[1].split(";")[0]
    file_name = str(uuid.uuid4())  # 隨機生成檔案名稱

    # 上傳 S3 的設定
    client.upload_fileobj(
        io.BytesIO(image_final),  # base64 編碼
        os.getenv("aws_bucketname"),  # buckent name
        file_name,
        ExtraArgs={"ContentType": image_header_final}  # 在S3上預覽，不下載
    )

    url = "https://d415c4pt97t76.cloudfront.net/" + file_name

    connection_object = connection_pool.get_connection()
    mycursor = connection_object.cursor()
    mycursor.execute(
        "INSERT INTO comment (message, url) VALUES (%s, %s)", (comment, url)
    )
    connection_object.commit()
    mycursor.close()
    connection_object.close()

    return {"data": True}, 200


@app.route("/showData", methods=["GET"])
def showData():
    # comment = request.json["comment"]
    # image = request.json["image"]
    connection_object = connection_pool.get_connection()
    mycursor = connection_object.cursor(dictionary=True)
    mycursor.execute("SELECT message, url FROM comment ORDER BY id DESC")
    myresult = mycursor.fetchall()

    details = []
    for result in myresult:
        detail = {
            "message": result["message"],
            "url": result["url"]
        }
        details.append(detail)

    mycursor.close()
    connection_object.close()

    return {"data": details}, 200


app.run(port=3000, host="0.0.0.0", debug=True)
