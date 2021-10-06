import os,sys
import json
import click
import requests
from rich import box
from rich.table import Table
from rich.syntax import Syntax
from rich.console import Console

console = Console()

gistAPI = "https://api.github.com/gists"
configFolderPath = os.path.expanduser('~') + os.sep +".config" + os.sep + "upgist"
configFileName   = "config.txt"
configFilePath   = configFolderPath + os.sep + configFileName

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

class GistFile():

    def __init__(self, description, public, fileName, content, fileID):
        self.fileID   = fileID
        self.postFile = {
                        "description" : description,
                        "public"      : public,
                        "files"       : {
                            fileName  : {
                                "content" : content if content != None else self.__GetContent(fileName),
                                }
                            }
                        }

    def __GetContent(self,fileName):
        file    = open(fileName,"r")
        content = file.read()
        file.close()
        return content

class Gist:

    def __init__(self):
        self.headers = {
                       "Authorization" : "token " + self.__GetToken()
                       }

    def GetGistRaw(self, gistID):
        fileList = []
        result   = requests.get(url=gistAPI + "/{gistID}".format(gistID=gistID),headers=self.headers)
        if self.__isError(result.status_code):
            console.print("[bold red][ERROR][/bold red] {errMsg}".format(errMsg=result.json()['message']))
            return                                                                                       
        gistInfo = result.json()                                                                          
        for file in gistInfo['files']:                                                                    
            gistFile = open(file,"w+")
            gistFile.write(gistInfo['files'][file]['content'])
            gistFile.close()

    def ViewGist(self, gistID):
        fileList = []
        result   = requests.get(url=gistAPI + "/{gistID}".format(gistID=gistID),headers=self.headers)
        if self.__isError(result.status_code):
            console.print("[bold red][ERROR][/bold red] {errMsg}".format(errMsg=result.json()['message']))
            return                                                                                       
        gistInfo = result.json()                                                                          
        table    = Table(box=box.ROUNDED,show_lines=True)                                                 
        table.add_column(":open_file_folder:files",style="cyan")                                          
        table.add_column(":memo:content",style="purple")                                                    
        for file in gistInfo['files']:                                                                    
            table.add_row(gistInfo['files'][file]['filename'],Syntax(gistInfo['files'][file]['content'], gistInfo['files'][file]['language'], theme="vim", line_numbers=True))
        return table

    def List(self,isShowID):
        result = requests.get(url=gistAPI,headers=self.headers)
        if self.__isError(result.status_code):
            console.print("[bold red][ERROR][/bold red] {errMsg}".format(errMsg=result.json()['message']))
            return
        if not isShowID:
            for gistInfo in result.json():
                table = self.ViewGist(gistInfo['id'])
                console.print(":link:[bold blue][link={url}]Gist ID[/link][/bold blue]: {gistID}".format(gistID=gistInfo.get('id'),url=gistInfo.get('html_url')))
                console.print(table)
        else:
            table = Table(box=box.ROUNDED,show_lines=True)
            table.add_column(":id:ID",style="blue")
            table.add_column(":open_file_folder:files",style="cyan")
            for gistInfo in result.json():
                fileNameList = []
                for file in gistInfo['files']:                                                                    
                    fileNameList.append(gistInfo['files'][file]['filename'])
                table.add_row("[link={url}]{gistID}[/link]".format(gistID=gistInfo.get('id'),url=gistInfo.get('html_url')),"\n".join(fileNameList))
            console.print(table)
            

    def Creat(self, file):
        result = requests.post(url=gistAPI,data=json.dumps(file.postFile),headers=self.headers)
        if self.__isError(result.status_code):
            console.print("[bold red][ERROR][/bold red] {errMsg}".format(errMsg=result.json()['message']))
            return
        console.print(":tada:[bold green]Successfully created[/bold green]: {url}".format(url=result.json()['html_url']))

    def Modify(self, file):
        result = requests.post(url=gistAPI + "/{id}".format(id=file.fileID), data=json.dumps(file.postFile), headers=self.headers)
        if self.__isError(result.status_code):
            console.print("[bold red][ERROR][/bold red] {errMsg}".format(errMsg=result.json()['message']))
            return
        console.print(":tada:[bold green]Successfully modify[/bold green] : {url}".format(url=result.json()['html_url']))

    def Delete(self, gistID):
        result = requests.delete(url=gistAPI + "/{gistID}".format(gistID=gistID),headers=self.headers)
        if self.__isError(result.status_code):
            console.print("[bold red][ERROR][/bold red] {errMsg}".format(errMsg=result.json()['message']))
            return

    def __isError(self, code):
        successCode = [200,201,204]
        return code not in successCode
    
    def __GetToken(self):
        file = os.path.exists(configFilePath)
        if not file:
            console.print("Pleace use the following command to set your token:\ngist config -tk YOUR_TOKEN")
            sys.exit(1)
        else:
            configFile = open(configFilePath,"r")
            token      = configFile.read()
            return token

def SaveToken(token):
    file = os.path.exists(configFolderPath)
    if not file:
        os.makedirs(configFolderPath)
    with open(configFilePath,"w") as configFile:
        configFile.write(token)
    configFile.close()

def PrintVersion(ctx,param,value):
    if not value or ctx.resilient_parsing:
        return
    print('Version 0.0.2')
    ctx.exit()

def Main_Options(f):
    version = click.option('--version',
                           '-v',
                           is_flag=True,
                           callback=PrintVersion,
                           expose_value=False,
                           is_eager=True)
    return version(f)

def Config_Options(f):
    token = click.option('--token',
                         '-tk',
                         'token',
                         nargs=1,
                         required=True,
                         multiple=False,
                         help="Set your token to client gist")
    return token(f)

def ViewGist_Options(f):
    gistid = click.option('--gistid',
                          '-id',
                          'gistID',
                          nargs=1,
                          required=True,
                          multiple=False,
                          help="View a gist by gist ID")
    return gistid(f)

def GetGistRaw_Options(f):
    gistid = click.option('--gistid',
                          '-id',
                          'gistID',
                          nargs=1,
                          required=True,
                          multiple=False,
                          help="Get a gist and save by gist ID")
    return gistid(f)

def DeleteGist_Options(f):
    gistid = click.option('--gistid',
                          '-id',
                          'gistID',
                          nargs=1,
                          required=True,
                          multiple=False,
                          help="Delete a gist by gist ID")
    return gistid(f)

def CreatGist_Options(f):
    file        = click.option('--file',
                               '-f',
                               'fileName',
                               nargs=1,
                               required=True,
                               multiple=False,
                               help="File name of gist")
    public      = click.option('--public',
                               '-p','public',
                               nargs=1,
                               default="true",
                               multiple=False,
                               type=click.Choice(["true", "false"]),
                               show_default=True,
                               help="Public of gist")
    content     = click.option('--content',
                               '-c',
                               'content',
                               nargs=1,
                               multiple=False,
                               help="Content of gist")
    description = click.option('--description',
                               '-d',
                               'description',
                               nargs=1,
                               default="From upgist by Fatpandac",
                               show_default=True,
                               multiple=False,
                               help="Description of gist")
    return file(public(content(description(f))))

def ModifyGist_Options(f):
    file        = click.option('--file',
                               '-f',
                               'fileName',
                               nargs=1,
                               required=True,
                               multiple=False,
                               help="Modify filename of gist")
    public      = click.option('--public',
                               '-p','public',
                               nargs=1,
                               default="true",
                               multiple=False,
                               type=click.Choice(["true", "false"]),
                               show_default=True,
                               help="Modify public of gist")
    content     = click.option('--content',
                               '-c',
                               'content',
                               nargs=1,
                               multiple=False,
                               help="Modify content of gist")
    description = click.option('--description',
                               '-d',
                               'description',
                               nargs=1,
                               default="From upgist by Fatpandac",
                               show_default=True,
                               multiple=False,
                               help="Modify description of gist")
    gistid      = click.option('--gistid',
                               '-id',
                               'gistID',
                               nargs=1,
                               required=True,
                               multiple=False,
                               help="Modify a gist by gist ID")
    return file(public(content(description(gistid(f)))))

def ListGist_Options(f):
    isShowID = click.option('--showid/--no-showid',
                            '-id/-nid',
                            'isShowID',
                            default=False,
                            show_default=True,
                            help="Just show gist id and filename")
    return isShowID(f)

@click.group(context_settings=CONTEXT_SETTINGS)
@Main_Options
def main():
    """Upgist is a gist cli tool."""

@main.command(name="config",help="Config upgist")
@Config_Options
def Config(token):
    SaveToken(token)

@main.command(name="get",help="Get a gist and save to the current directory")
@GetGistRaw_Options
def GetGistRaw(gistID):
    gist = Gist()
    gist.GetGistRaw(gistID)

@main.command(name="view",help="Just view a gist is not saved")
@ViewGist_Options
def ViewGist(gistID):
    gist = Gist()
    console.print(gist.ViewGist(gistID))

@main.command(name="modify",help="Modify a gist")
@ModifyGist_Options
def ModifyGist(gistID,fileName,content,description,public):
    gist = Gist()
    file = GistFile(description=description, public=public, fileName=fileName, content=content,fileID=gistID)
    gist.Modify(file)
    
@main.command(name="delete",help="Delete a gist")
@DeleteGist_Options
def DeleteGist(gistID):
    gist = Gist()
    gist.Delete(gistID)

@main.command(name="list",help="Show all your gist")
@ListGist_Options
def GistList(isShowID):
    gist = Gist()
    gist.List(isShowID)

@main.command(name="create",help="Create a gist")
@CreatGist_Options
def CreatGist(fileName,content,description,public):
    gist = Gist()
    file = GistFile(description=description, public=public, fileName=fileName, content=content,fileID=None)
    gist.Creat(file)

if __name__ == "__main__":
    main()
