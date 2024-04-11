import pickle
import os.path
from google.auth.transport.requests import Request 
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import logging

SCOPES = ["https://www.googleapis.com/auth/drive"]

logging.basicConfig(filename='backup.log', level=logging.INFO ,  format='%(asctime)s - %(message)s')


#------------------------------------------------------------------------------------------
'''
Authorization and Authentication 
'''
def Authnenticate() :
	creds = None

	if os.path.exists("token.pickle"):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)

	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else: 
			flow = InstalledAppFlow.from_client_secrets_file("credentials_cc.json",SCOPES)
			creds = flow.run_local_server(port = 0)
				
		with open("token.pickle","wb") as token:
			pickle.dump(creds,token)
	
	return creds

# ----------------------------------------------------------------------------------------

'''
Try to Access Google Drive using API 
'''
def Upload_Folder(service):
	try:
		logging.info('Starting upload process')
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
		
		for file in os.listdir('backup-dir'):
			existing_files = service.files().list(q=f"name = '{file}' and '{folder_id}' in parents",spaces='drive').execute().get('files',[])

			if existing_files:
				print(f"File '{file}' already exists in Google Drive. Skipping...")
				logging.info(f"File '{file}' already exists in Google Drive. Skipping...")


				continue
			file_metadata = { 
				"name":file,
				"parents":[folder_id],
			}

			media =	MediaFileUpload(f"backup-dir/{file}")
			upload_file = service.files().create(body=file_metadata,media_body=media,fields="id").execute()
			print("Backed up file : ",file)
			logging.info(f"Backed up file : {file}")

		
		logging.info('Upload process completed successfully')

	except HttpError as e:
		 logging.error(f'Error occurred during upload process: {str(e)}')

#----------------------------------------------------------------------------------------------------------------
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
#     # TODO(developer) - Handle errors from drive API.
		  print(f"An error occurred: {error}")


def main():
	creds = Authnenticate()
	service = build("drive","v3",credentials=creds)
	logging.info('Backup process started')
	Upload_Folder(service)
	logging.info('Backup process completed')
	List_Files(creds,service,"root")



if __name__ =="__main__":
	main()



