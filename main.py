import os
import os.path
from google.auth.transport.requests import Request 
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import io

SCOPES = ["https://www.googleapis.com/auth/drive"]



#------------------------------------------------------------------------------------------
'''
Authorization and Authentication 
'''
def Authnenticate() :
	creds = Credentials.from_service_account_file("cronkube-service.json",scopes=SCOPES)
	
	return creds

# ----------------------------------------------------------------------------------------

'''
Try to Access Google Drive using API 
'''
def Upload_Folder(service):
	try:
		response = service.files().list(
			q = "name='BackupFolder24' and mimeType='application/vnd.google-apps.folder'",
			spaces = 'drive'
		).execute()

		if not response['files']:
			file_metadata = {
				"name":"BackupFolder24",
				"mimeType":"application/vnd.google-apps.folder",
			}

			file = service.files().create(body=file_metadata,fields="id").execute()

			folder_id = file.get('id')

		else :
			folder_id = response['files'][0]['id']
		
		for file in os.listdir('./backup-dir'):
			existing_files = service.files().list(q=f"name = '{file}' and '{folder_id}' in parents",spaces='drive').execute().get('files',[])

			if existing_files:
				print(f"File '{file}' already exists in Google Drive. Skipping...")
				continue
			file_metadata = { 
				"name":file,
				"parents":[folder_id],
			}

			media =	MediaFileUpload(f"../backup-dir/{file}")
			upload_file = service.files().create(body=file_metadata,media_body=media,fields="id").execute()
			print("Backed up file : ",file)


	except HttpError as e:
		print("Error:"+str(e))

#----------------------------------------------------------------------------------------------------------------
'''
List the drive with folders to access
'''
def List_Files(creds,service,file_id,indent = ' '):
	try:
		response = service.files().list(q=f"'{file_id}' in parents", fields="files(id,name, mimeType)").execute()
		files = response.get("files",[])

		if not files:
			print("No files found.")
			return
		
		for file in files:
			if file['mimeType'] == 'application/vnd.google-apps.folder':
				print(f"{indent}{file['name']} -")
				List_Files(creds,service, file['id'], indent + '    ')
			else:
				
				print(f"{indent}{file['name']}")
	except HttpError as error:
		  print(f"An error occurred: {error}")


#----------------------------------------------------------------------------
'''
Search a folder or file by Name
'''
def get_folder_id(service,folder_name):
	try:
		response = service.files().list(
			q = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
			fields="files(id, name)"
		).execute()
		items = response.get('files',[])
		#print("GET-FOLDER-ID ",items[0]['id'])
		if items:
			return items[0]['id']
		else:
			return None
	except HttpError as e:
		print(f"An error occurred: {e}")


def get_file_by_id(service,file_name):
	try:
		response = service.files().list(
			q=f"name='{file_name}'",
			fields="files(id, name)"
		).execute()
		items = response.get('files', [])
		if items:
			return items[0]['id']
		else:
			print("File not found.")
			return None
	except Exception as e:
		print(f"An error occurred: {e}")
		return None
#-------------------------------------------------------------------------------------------------------------------
'''
delete a folder by Name
'''
def delete_folder(folder_name,service):
	
	folder_id = get_folder_id(service,folder_name)
	try:
		service.files().delete(fileId=folder_id).execute()
		print("Folder deleted successfully.")
	except HttpError as e:
		print(f"An error occurred: {e}")
	else:
		print("Folder not found.")
	
#----------------------------------------------------------------------------------------------------------------	
'''
delete a file by its name
'''
def delete_file(file_name,service):
	
	file_id = get_file_by_id(service,file_name)
	try :
		service.files().delete(fileId=file_id).execute()
		print("File deleted successfully.")
	except HttpError as e:
		print(f"An error occurred: {e}")
	else:
		print("File not found.")
#-----------------------------------------------------------------------------------------------------------------	


def main():
	creds = Authnenticate()
	service = build("drive","v3",credentials=creds)
	Upload_Folder(service)
	List_Files(creds,service,"root")
	# delete_folder("BackupFolder24",service)
	# delete_file("another-file.txt",service)
	# folder_id = get_folder_id(service,"BackupFolder24")
	#List_Files(creds,service,"root")



if __name__ =="__main__":
	main()



