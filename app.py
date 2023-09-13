from flask import Flask, render_template, request, flash
import boto3, botocore

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'

s3 = boto3.client("s3")
s3_resource = boto3.resource('s3')


#---------------------------Home Page---------------------------
@app.route('/')
def home_page():
    return render_template('index.html')


#---------------------------Listing S3 buckets---------------------------
@app.route('/list')
def list_buckets():
    listOfBuckets = []
    for bucket in s3_resource.buckets.all():
        listOfBuckets.append(bucket.name)
    if len(listOfBuckets) == 0:
        flash('No Buckets!!')
    return render_template('list.html',listOfBuckets=listOfBuckets)


#---------------------------Create/delete bucket---------------------------
@app.route('/bucketForm')
def bucket_form():
    return render_template('bucketForm.html')

#Create Bucket
@app.route('/createBucket',methods=['POST'])
def create_bucket():
    bucketName = request.form.get('bucketName')
    try:
        s3.create_bucket(
            ACL='private',
            Bucket=bucketName,
            CreateBucketConfiguration={'LocationConstraint': 'ap-south-1'}
        )
    except:
        flash("Bucket already exists, Try another name!!")
    return render_template('bucketForm.html')

#Delete Bucket
@app.route('/delBucket',methods=['POST'])
def delete_bucket():
    bucketName = request.form.get('bucketName')
    try:
        s3.delete_bucket(
            Bucket= bucketName
        )
    except botocore.exceptions.ClientError:
        flash('This bucket is either not empty or not exists!!')
    return render_template('bucketForm.html')


#---------------------------Create/delete folder---------------------------
@app.route('/folderForm')
def folder_form():
    return render_template('folderForm.html')

#Creating folder
@app.route('/create',methods=['POST'])
def create_folder():
    bucketName = request.form.get('bucketName')
    folderName = request.form.get('folderName')+'/'
    try:
        bucket = s3_resource.Bucket(bucketName)
        bucket.put_object(Key=folderName)
        for obj in bucket.objects.all():
            if obj.key == folderName:
                flash('Folder was created successfully!')
    except:
        flash('No such Bucket!!')
    return render_template('folderForm.html')

#Delete Folder
@app.route('/delete',methods=['POST'])
def delete_folder():
    bucketName = request.form.get('bucketName')
    folderName = request.form.get('folderName') + '/'
    try:
        objects = s3.list_objects(Bucket=bucketName, Prefix=folderName)
        files_in_folder = objects["Contents"]
        files_to_delete = []
        for f in files_in_folder:
            files_to_delete.append({"Key": f["Key"]})
        s3.delete_objects(
            Bucket=bucketName, Delete={"Objects": files_to_delete}
        )
    except botocore.exceptions.ClientError:
        flash('No such bucket!!')
    except KeyError:
        flash('No such folder!!')
    return render_template('folderForm.html')


#---------------------------Uploading file to S3---------------------------
@app.route('/uploadForm')
def form():
    return render_template('uploadForm.html')

@app.route('/upload', methods=["POST"])
def upload():
    bucketName = request.form.get('bucket')
    file = request.files['file']
    try:
        fileName = file.filename
        s3.upload_fileobj(file,bucketName,fileName)
    except botocore.exceptions.ClientError:
        flash('No such bucket!!')
    return render_template('uploadForm.html')


#---------------------------Delete file from S3---------------------------
@app.route('/delFileForm')
def del_file_form():
    return render_template('delFileForm.html')

@app.route('/delFile',methods=['POST'])
def delFile():
    bucketName = request.form.get('bucketName') 
    fileName = request.form.get('fileName')
    try:
        s3.delete_object(Bucket=bucketName, Key=fileName)
    except botocore.exceptions.ClientError:
        flash('No such bucket!!')
    return render_template('delFileForm.html')


#---------------------------Copy/Move file within S3---------------------------
@app.route('/moveForm')
def move():
    return render_template('moveForm.html')

#Copy file within s3
@app.route('/copy',methods=['POST'])
def copy_s3_objects():
    sourceBucket = request.form.get('sourceBucket')
    sourceFile = request.form.get('sourceFile')
    destBucket = request.form.get('destBucket')
    destFile = request.form.get('destFile')
    try:
        copy_source = {
            'Bucket': sourceBucket,
            'Key': sourceFile
        }
        s3_resource.meta.client.copy(copy_source, destBucket, destFile)
    except botocore.exceptions.ClientError:
        flash('You have entered wrong details!!')
    return render_template('moveForm.html')

#Move file within s3
@app.route('/move',methods=['POST'])
def move_files():
    sourceBucket = request.form.get('sourceBucket')
    sourceFile = request.form.get('sourceFile')
    destBucket = request.form.get('destBucket')
    destFile = request.form.get('destFile')
    try:
        copy_source = {
            'Bucket':sourceBucket,
            'Key':sourceFile
        }
        s3_resource.meta.client.copy(copy_source, destBucket, destFile)
        s3.delete_object(
            Bucket=sourceBucket,
            Key=sourceFile
        )
    except botocore.exceptions.ClientError:
        flash('You have entered wrong details!!')
    return render_template('moveForm.html')


if __name__ == "__main__":
    app.run(debug=True)