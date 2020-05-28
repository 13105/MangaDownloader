import tkinter as tk
import sys, urllib.request, time, os, hashlib
from tkinter import filedialog,messagebox,ttk
from urllib.request import urlopen
from threading import Thread
from pathlib import Path



DOWNLOAD_DELAY_S = 2 # segundos de espera antes de baixar a proxima pagina

root = tk.Tk()
arqAlbl = tk.StringVar()
arqNomelbl = tk.StringVar()
statuslbl = tk.StringVar()
progress = ttk.Progressbar(orient=tk.HORIZONTAL, mode="determinate",length=350)

def GetBaixada(jaBaixadas, capitulo, pagina):
    for jbi in jaBaixadas:
        if (capitulo == jbi[0]) and (pagina == jbi[1]) :
            return jbi

def ChecarBaixadas(o_dir):
    bfLista = []

    bfDir = os.path.join(o_dir, "baixadas.txt")
    if not os.path.exists(bfDir):
        return

    try:
        with open(bfDir,"r") as bf:
            bfLinhas = bf.readlines()
        for bfLinha in bfLinhas:
            bfLista.append(bfLinha.split("\x00"))
        return bfLista

    except Exception as e:
        return

def Baixar(conteudo, o_dir):

    print("[  *  ] Iniciando procedimento de download...")
    PARTE =  113 * 1024 # 100KB ;1MB = 1024KB
    n_BaixadasL = []
    totalPaginas = 0

    jaBaixadas = ChecarBaixadas(o_dir)

    #bf = baixadas file; baixadas.txt
    bf = open(os.path.join(o_dir, "baixadas.txt"),"a")


    for item in conteudo: #cada linha;

        BaixadasL = []
        #itens separados por delimitador
        cLinha = item.split("\x00")
        epNum = cLinha[0]
        epNome = cLinha[1]
        f_dir = o_dir



        #total de paginas baixadas
        totalPaginas += len(cLinha[2:-1])

        #Cada url contendo imagem do capitulo
        for iPagina, url in enumerate(cLinha[2:-1]):



            NomeArq = str(iPagina+1) + ".jpg"
            pagina = str(iPagina+1)

            arqNomelbl.set("Capítulo: {}, página: {}; {}".format(epNum, pagina, epNome ))

            if(jaBaixadas):


                ljb = GetBaixada(jaBaixadas, epNum, pagina)

                if ljb:
                    print("[ ... ] Página {0} ({1} KB) do capítulo {2} já foi baixada...".format(ljb[1], round(int(ljb[2]) / 1024), ljb[0] ))
                    continue;

            urlReq = url


            req = urllib.request.Request(urlReq)

            req.add_header("Accept","text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
            req.add_header("Accept-Encoding","gzip, deflate, br")
            req.add_header("Accept-Language","pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3")
            req.add_header("User-Agent","Mozilla/5.0 (Windows NT 10.0; rv:70.0) Gecko/20100101 Firefox/70.0")
            try:

                #time.sleep(DOWNLOAD_DELAY_S)
                resposta = urlopen(req)

                if(resposta.getcode() == 429):

                    time.sleep(int(resposta.getheader("Retry-After")))
                    resposta = urlopen(req)



                tamanhoTotal = int(resposta.getheader("Content-Length"))




                sha1 = hashlib.sha1()


                progress["maximum"] = tamanhoTotal
                progress["value"] = 0




                if not os.path.exists( Path(os.path.join(o_dir, str(epNum) ))):
                    os.mkdir( Path(os.path.join(o_dir, str(epNum))))

                f_dir = Path(os.path.join(o_dir, str(epNum)))


                arq_dir = os.path.join(f_dir, NomeArq)

                with open(arq_dir, "wb") as f:
                    while True:

                        parte = resposta.read(PARTE)

                        if not parte:
                            break


                        f.write(parte)
                        sha1.update(parte)


                        progress["value"] += len(parte)
                        arqAlbl.set(" %s / %s" %( progress["value"],tamanhoTotal))
                        statuslbl.set("[ {0:.0%} ] Baixando...".format((progress["value"] / tamanhoTotal) ) )
                        sys.stdout.write("\r[ {0:.0%} ] Baixando {1}...".format((progress["value"] / tamanhoTotal),NomeArq ))
                        sys.stdout.flush()

                BaixadasL.append([epNum, str(pagina), str(tamanhoTotal),sha1.hexdigest()])
                print("OK")

                #----------------

                print(" ____________________________________________________________________________________\n| Capítulo: {} -> página {} \tBaixado\n| SHA1:\t\t\t\t{}\n| Tamanho (Bytes):\t\t{} B\n| Tamanho (Kilo Bytes):\t\t{} KBs\n| Tamanho (Mega Bytes):\t\t{} MBs\n| Diretório:\t{}\n| URL:\t\t{}\n|____________________________________________________________________________________\n".format(
                epNum,
                pagina,
                sha1.hexdigest(),
                tamanhoTotal,
                round(tamanhoTotal / 1024),
                round(tamanhoTotal / 1024 / 1024,2),
                arq_dir,
                url))


            except Exception as e:

                statuslbl.set(e)
                progress["value"] = 0
                arqAlbl.set(" 0 / 0")
                print("\r[  !  ] Error: Capítulo {0}, página {1}: {2}.".format(epNum, pagina,  str(e) ))




                n_BaixadasL.append([epNum, pagina, cLinha[1], str(e)])



                pass




        if(len(BaixadasL) > 0):

            #salva log de baixadas para não precisar baixar dnv
            for baixada in BaixadasL:
                bf.write(baixada[0]+"\x00"+baixada[1]+"\x00"+baixada[2]+"\x00"+baixada[3]+"\n")

    bf.close()

    nBaixadasCount = len(n_BaixadasL)
    nBaixadasArq = os.path.join(o_dir, "Páginas não baixadas.txt")

    #Salva não baixadas para informação do usuário
    if(len(n_BaixadasL) > 0):


        print("[  *  ] Registrando {} página(s) não baixada(s)...".format(nBaixadasCount))
        statuslbl.set("Registrando %s página(s) não baixada(s)...".format(nBaixadasCount))
        with open(nBaixadasArq, "w", encoding="utf-8") as nbf: #nao baixadas file
            for inb in n_BaixadasL: #item não baixado
                nbf.write("Capítulo {0}, página {1};{2}; Erro: {3};\n".format(inb[0], inb[1], inb[2],inb[3] ))
        statuslbl.set("páginas não baixadas registradas !")

    else:
        if os.path.exists(nBaixadasArq):
            os.remove(nBaixadasArq)


    statuslbl.set("{} / {} páginas baixadas".format( (totalPaginas - nBaixadasCount), totalPaginas))
    print("--------------------------\n{} / {} páginas baixadas".format( (totalPaginas - nBaixadasCount), totalPaginas  ))
    print("\nFim.");
    statuslbl.set("Fim")

def iniciarProc(conteudo, o_dir):
    Thread(target=Baixar, args=(conteudo, o_dir,)).start()
    ## TODO: ADICIONAR MAIS THREADS PARA TRABALHAR BAIXANDO PARTES DIVIDIDAS EM CAPITULOS DE FORMA ASSÍNCRONA

def main():

    root.title("Subdl")
    root.withdraw()

    if len(sys.argv) < 2:
        messagebox.showerror("MDL","Arquivo MDL não especificado.")
        sys.exit()
    try:
        with open(sys.argv[1]) as f:
            conteudo = f.readlines()


        pass

    except FileNotFoundError as e:
        messagebox.showerror("MDL","Arquivo contendo a lista de links não encontrado.")
        sys.exit()





    if len(conteudo) < 1:
        messagebox.showerror("MDL","Nenhum capitulo foi especificada na lista.")
        sys.exit()

    # index 0 = reservado para nome da serie
    o_dir = filedialog.askdirectory() #output dir; diretorio de saida

    #Debug:
    #o_dir = "C:\\Users\\13105\\Documents\\DEV\\WEB\\MangaLivreDownloader"
    if len(o_dir) <= 0:
        messagebox.showerror("MDL","Diretorio para salvar paginas não especificado.")
        sys.exit()

    arqNome = sys.argv[1].split(".")[0]




    if not os.path.exists(Path(os.path.join(o_dir, os.path.basename(arqNome)))):
        os.mkdir(Path(os.path.join(o_dir, os.path.basename(arqNome))))

    o_dir = Path(os.path.join(o_dir, os.path.basename(arqNome)))


    if not os.path.isdir(str(o_dir)):
        messagebox.showerror("MDL","Diretorio especificado invalido.")
        sys.exit()

    root.iconbitmap(os.path.join(os.getcwd(),"sat.ico"))
    root.geometry("370x100")
    root.resizable(width=False,height=False)
    root.deiconify()






    progress.pack()

    #define propriedades dos controladores
    tk.Label(root,textvariable=arqAlbl,font=("Arial",9)).pack()
    arqAlbl.set("-")

    tk.Label(root,textvariable=arqNomelbl,font=("Helvetica",10)).pack()

    tk.Label(root,textvariable=statuslbl,font=("Arial",8)).pack()

    iniciarProc(conteudo, o_dir)
    root.mainloop()

if __name__ == "__main__":
    main()
