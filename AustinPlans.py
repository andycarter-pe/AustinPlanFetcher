#
#Note that this uses the TestEnv3 setup - MAC - 2020.04.17
#
"""
City of Austin Plan Fetcher - 2020.04.23
Created by:  Andy Carter, PE
    LandDev Consulting, LLC
    4201 W. Parmer Ln, Suite C-100 
    Austin, Texas 78727 
    (o) 512.872.6696 x634 
    andy.carter@landdevconsulting.com

Last Revised:  23 April 2020

Purpose: This script allows a user to download all construction plans sheets
from a provided City of Austin RSN file folder. Typically a RSN folder number
is obtained from the City of Austin's Austin Build + Connect website.

All sheets (with a ~ in the file name) are downloaded.  Sheets that are tif's
are converted to pdf's.  All the downloaded sheets are merged into a single
file pdf.
"""

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import PhotoImage

from myimages import *

import webbrowser

import glob 
import os                          #operating system
import re                          #regular expressions
from PyPDF2 import PdfFileMerger   #Used for merging PDFs

import img2pdf                     #Converting TIF to PDF

import requests                    #For making HTML requests
from bs4 import BeautifulSoup      #For parsing and searching the returned HTML
import urllib

from multiprocessing.pool import ThreadPool  #threadpool to multi-thread the downloading of the multiple files (for speed)

#**********************************************
root = Tk()
root.title('Austin Build + Connect Plan Fetcher')
root.geometry("735x300") #Size of the form - 250
root.resizable(0, 0) #Don't allow resizing in the x or y direction

picLandDev = imgLandDevString #GIF decoded to string. imageString from myimages.py
renderLandDev = PhotoImage(data=picLandDev)
renderLandDev = renderLandDev.subsample(3, 3) # divide by 3

picBatImage = imgBatImageString #GIF decoded to string. imageString from myimages.py
renderBatImage = PhotoImage(data=picBatImage)
renderBatImage = renderBatImage.subsample(3, 3) # divide by 3

root.wm_iconphoto(True, renderBatImage)
url = 'https://www.landdevconsulting.com/'
url_2 = 'https://www.austintexas.gov/GIS/PropertyProfile/'

def OpenUrl(url):
    webbrowser.open_new(url)

def CityUrl(url_2):
    webbrowser.open_new(url_2)

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

def funcDownloadFile(fileURL):
    req = urllib.request.Request(fileURL, method='HEAD')
    r = urllib.request.urlopen(req)
    if r.info().get_filename() is not None:
        # Uses content deposition to get the file name of the download
        strFilePath = strIndexPath + "\\" + r.info().get_filename()
        # add to fileList for clean-up
        fileList.append(strFilePath)
        r = requests.get(fileURL)

        with open(strFilePath, 'wb') as f:
            f.write(r.content)
            f.close()

def merger(output_path, input_paths):
    pdf_merger = PdfFileMerger()
    file_handles = []
    
    for path in input_paths:
        pdf_merger.append(path)
        
    with open(output_path, 'wb') as fileobj:
        pdf_merger.write(fileobj)
        pdf_merger.close()

def scandirs(path):
    for root, dirs, files in os.walk(path):
        for currentFile in files:
            #Delete only the files that are in the fileList
            strTotalPath = root + "\\" + currentFile
            if strTotalPath in fileList:
                os.remove(os.path.join(root, currentFile))

def cbuttBrowseClick():
    eFilePath1.delete(0, END)
    global strFileDirectory
    strFileDirectory = filedialog.askdirectory(mustexist=TRUE)
    eFilePath1.insert(0, strFileDirectory)
    statusLabel['text'] = ""
    
def cbuttGetSet():
    # Requested Folder RSN number
    fltFolderNumber = eRSN.get()

    # Path to folder holding all the downloaded PDFs 
    global strIndexPath 
    strIndexPath = eFilePath1.get()

    strFolderNumber = str(fltFolderNumber)
    strFolderNumber = strFolderNumber.replace(" ", "") # remove spaces from RSN

    # URL to the City of Austin permit sets
    strPermitPath = r"https://abc.austintexas.gov/web/permit/public-search-other?t_detail=1&t_selected_folderrsn="
    
    statusLabel['text'] = "Making request to City of Austin server...Stand By..."
    root.update()
    url =  requests.get(strPermitPath + strFolderNumber)
    soup = BeautifulSoup(url.text, 'html.parser')

    #Check to see if there is a folder returned
    y = soup.find('span', text=" No Rows Returned ")
    if y != None:
        statusLabel['text'] = "City of Austin RSN does not exist"
        root.update()
    else:
        # Get all the download-able links with the class ="download-url" in the webpage HTML
        download_file_list = soup.find_all(class_='download-url')

        # Strip just the link (http:\\....) from the href tag for each record in download_file_list
        #  Put these links into the urllist array
        urlList = []
        for htmlblock in download_file_list:
            urlList.append(htmlblock.get('href'))
    
        statusLabel['text'] = "City of Austin server request complete...Beginning Download..."
        root.update()
	
        global fileList
        fileList = []

        intFileCount = len(download_file_list)
        i=0

        results = ThreadPool(40).imap_unordered(funcDownloadFile, urlList)

        for strFileToDownload in results:
            #TODO - Error as City may have unnamed files in the download list - 2020.03.26
            i += 1
            statusLabel['text'] = ('Downloading Documents: ' + str(i) + " of " + str(intFileCount))
            root.update()
    
        statusLabel['text'] = "Downloading Complete."
		
	    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	    #Find all files that are downloaded that have a tilde '~' and are tif's
        search_criteria = "*[~]*.tif"
        strTifList = os.path.join(strIndexPath, search_criteria)
        tif_files = glob.glob(strTifList)
        tif_files.sort()

        if len(tif_files) > 0:
            j=0
            #Converting TIF files.
            for i in tif_files:
                j += 1
                statusLabel['text'] = ('Converting TIFs to PDFs: ' + str(j) + " of " + str(len(tif_files)))
                root.update()
                #output_file = ''.join(i.split())[:-4] + ".pdf"
                output_file = i[:-4] + ".pdf"
				#This split is erroring out on space in name - 2020.04.17
                #add to fileList for clean-up
                fileList.append(output_file)
                pdf_bytes = img2pdf.convert(i)
                file = open(output_file,"wb")
                file.write(pdf_bytes)
                file.close()
	    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	
        #Find all file that are downloaded that have a tilde '~' and are pdf's
        statusLabel['text'] = "Merging Sheets into single PDF"
        root.update()
        search_criteria = "*[~]*.pdf"
        q = os.path.join(strIndexPath, search_criteria)
        pdf_files = glob.glob(q)
        pdf_files.sort()

        #Get the project name: 
        if len(pdf_files) > 0:
            #Parse what is left of the tilde '~' of the first sheet
            s = pdf_files[0]
            j = s[0:s.find('~')]
            #print(j) #This is the full path of the first sheet

            #Split up j into an array 'a'; Split on the '\'
            a=(j.split('\\'))
            strCaseNumber = (a[-1])

            #The name of the file to write out
            strOutPath = strIndexPath + "\\" + strCaseNumber + "_Merge.pdf"

            merger(strOutPath, pdf_files)
            statusLabel['text'] = ('Project Plan Set Created: ' + strCaseNumber + '_Merge.pdf')
            root.update()
        else:
            statusLabel['text'] = ('No plan sheets found in RSN folder')
            root.update()
    
        #Clean up the download folder
        #statusLabel['text'] = "Cleaning Download Directory"
        #root.update()
        scandirs(strIndexPath)
	

#------------------------
myLabel0 = Label(root, text="       ")
myLabel0.grid(row=0, column=0 )

#------------------------
myLabel1 = Label(root, text="File Path:", font='Helvetica 9 bold')
myLabel1.grid(row=1, column=0, sticky="E" )

eFilePath1 = Entry(root, width=90, borderwidth = 3)
eFilePath1.grid(row=1, column=1, padx=10, pady=5, sticky="W")

myButton1 = Button(root, text="Browse...", command=cbuttBrowseClick)
myButton1.grid(row=1, column=2, padx=5)

#------------------------
myLabel2 = Label(root, text="   City RSN#:", font='Helvetica 9 bold')
myLabel2.grid(row=2, column=0, sticky="E" )

eRSN = Entry(root, width=15, borderwidth = 3)
eRSN.grid(row=2, column=1, padx=10, pady=5, sticky="W")

myButton2 = Button(root, text="Web Site", command=lambda aurl=url_2:CityUrl(aurl))
myButton2.grid(row=2, column=2, padx=5)

#------------------------
myButton3 = Button(root, text="Get Plan Set", command=cbuttGetSet, font='Helvetica 12 bold')
myButton3.grid(row=3, column=1, padx=5)
#------------------------
myLabel4 = Label(root, text="--------------------------------------------------------------------------------------------------")
myLabel4.grid(row=4, column=0, columnspan=3)
#------------------------
myLabel5 = Label(root, text="Status:", font='Helvetica 9 bold')
myLabel5.grid(row=5, column=0, sticky="E")

statusLabel = Label(root, text="Select a path where plans will be downloaded")
statusLabel.grid(row=5, column=1,)
#------------------------
myLabel6 = Label(root, text="--------------------------------------------------------------------------------------------------")
myLabel6.grid(row=6, column=0, columnspan=3)
#------------------------
myButton7 = Button(root, image=renderLandDev, command=lambda aurl=url:OpenUrl(aurl))
myButton7.grid(row=7, column=1, padx=5)

myLabel7 = Label(root, image=renderBatImage)
myLabel7.grid(row=7, column=0, sticky="E" )
#------------------------
myLabel8 = Label(root, text="Created by Andy Carter, PE - LandDev Consulting - April 2020", font='Helvetica 8')
myLabel8.grid(row=8, column=0, columnspan=3)
#------------------------

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

	
	
