

var btn = document.createElement("span");
var lbl = document.createElement("label");
btn.textContent = "Baixar tudo";
btn.className = "mldBtn";

lbl.className = "mldLbl";
var parser = new DOMParser();


async function getCapitulosLista(pagina, id_serie){

    var url = `https://mangalivre.com/series/chapters_list.json?page=${pagina}&id_serie=${id_serie}`;

    return fetch(url,
    {
      headers:{'X-Requested-With':'XMLHttpRequest'}
    }

    ).then(function(arg){
        return arg.json();
    }).then(function(dados){
        return dados.chapters;
    });

}


//requisita a primeira pagina para calcular o tamanho total

//id vindo da url
async function getArrCapitulos(){
serie_id = window.location.pathname.split("/")[3];
var capitulos = await getCapitulosLista(1, serie_id);
var total_capitulos = capitulos[0].number;


  var iPagina = 1;
  while (capitulos.length < total_capitulos) {
      iPagina++;
      capitulos = capitulos.concat(await getCapitulosLista(iPagina, serie_id));
  }

  return capitulos;
}



async function getCapituloJson(url_ep){

  // retorna url do json
  return await fetch(url_ep).then(function(res) {
    			return res.text();
  			}).then(function(ret){
            pagina = parser.parseFromString(ret, "text/html");
  					return pagina;
          }).then(function(pagina){
            var scriptTags = pagina.getElementsByTagName("script");
            var scriptTag;
            //vasculha scripts à procura do token

						for(const tag of scriptTags){
  							if(tag.attributes.src){
    								if(tag.attributes.src.value.includes("token")){
    								   scriptTag = tag.attributes.src.value;
    								}
  							}
            }

            if(!scriptTag){
              lbl.textContent = `Erro: Não foi possível identificar o Token na url: ${url_ep} !`;
              console.log(`Erro: Não foi possível identificar o Token na url: ${url_ep} !`);
              return;
            }

            let token = scriptTag.split("&")[1].split("=")[1];
            let id = scriptTag.split("&")[2].split("=")[1];
            let json_imgs = "https://mangalivre.com/leitor/pages/"+ id +".json?key=" + token;

            return json_imgs;
          });

  }




async function old_getPaginas(json_url){
  var img_lista = [];
  //retorna lista de blobs
  return await fetch(json_url).then(function(res) {
        //acessa e analisa o json
          return res.json();
        }).then(function(jsonArr){

          //console.log(jsonArr);

            //baixa as imagens com base nas urls especificadas no json
            for(var i=0;i < jsonArr.images.length; i++){


                img_lista.push(
                    fetch(jsonArr.images[i]).then(function(imgbuffer) {
                     return imgbuffer.arrayBuffer();
                     })
                );

            }

            //quando todas as imagens forem baixadas, retornar array de blobs
            return Promise.all(img_lista).then((ret) => {
              return ret;
            });

          });



 }

async function getPaginas(json_url){
  //retorna uma array de jsons
    return fetch(json_url).then(
            function(res) {
                //acessa e analisa o json
                return res.json();
            }
    ).then(

              function(jsonArr){
                    return jsonArr.images;
                }
    );

}

async function getListas(lista){

      if (!lista){
        console.log("Erro: Nenhum link na lista !");
        return;
      }





      //array para nome, numero e lista de urls
      var arrPaginasUrls = [];

      for(var i = lista.length-1;i >= 0; i--){

        // array de promessas


            var epNum = lista[i]["number"]
            var epName = lista[i]["chapter_name"];



            let releasesObj = lista[i]["releases"];
            let lerUrl = "https://mangalivre.com" + releasesObj[Object.keys(releasesObj)[0]]["link"];



            let jsonUrl = await getCapituloJson(lerUrl);





            arrPaginasUrls.push([
              epNum,
              epName,
              await getPaginas(jsonUrl)  // Promessa que retorna array de urls para imagens
            ]);


            //porcentagem
            let prc = Math.abs(Math.round( ( (i- lista.length-1) / lista.length ) * 100));
            lbl.textContent = `Coletando URLs ${prc}% ...`;







      }


      var arq_dados="";
      //Converte conteudo em texto


      for (dados of arrPaginasUrls) {
        arq_dados = arq_dados.concat(dados[0],"\x00",dados[1],"\x00");
        for (urlImg of dados[2]) {

            arq_dados = arq_dados.concat(urlImg,"\x00");
        }

        arq_dados += "\n";
      }

    lbl.textContent = "Gerando arquivo...";
    var arq = new Blob([arq_dados], {type: "application;MDL"});
    saveAs(arq, window.location.pathname.split("/")[2].concat(".mdl"));

    lbl.textContent = "Fim";


  }


async function btn_click(e){

    var capitulos = await getArrCapitulos()


    getListas(capitulos);

    e.target.style.borderColor = "#8c8a8a";
    e.target.style.color = "#424242";
    e.target.removeEventListener("click", btn_click);



    return;

}


btn.addEventListener("click", btn_click);
var div = document.querySelector("#series-data");
div.appendChild(btn);
div.appendChild(lbl);

//var zip = new JSZip();
//zip.file("Hello.txt", "Hello World\n");
//var img = zip.folder("images");

//img.file("smile.gif", imgData, {base64: true});
//console.log(zip);
//zip.generateAsync({type:"blob"}).then(function(content) {
//    saveAs(content, "example.zip");
//});
//alert(1);
