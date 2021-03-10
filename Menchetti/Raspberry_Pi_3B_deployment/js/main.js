function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            document.getElementById("span_risultato").innerHTML = "";
            $('#preview').attr('src', e.target.result);
        }

        reader.readAsDataURL(input.files[0]);
    }
}

function rilevaRazza() {
    document.getElementById("span_risultato").innerHTML = "";

    var fd = new FormData();
    var files = document.getElementById("file").files;

    // Check file selected or not
    if(files.length > 0 ){
       fd.append('file',files[0]);

       document.getElementById("span_button").innerHTML = "<img src='img/loading.gif' width='100' height='100'/><br>"
       $.ajax({
          url: 'server.php',
          type: 'POST',
          data: fd,
          contentType: false,
          processData: false,
          async: true,
          timeout: 0,
          success: function(response){
             if(response != 0){
                if(response.includes("Errore")){
                  alert(response);
                } else {
                  document.getElementById("span_risultato").innerHTML = "<p style='font-weight: bold'>"+response+"</p>";
                }
             }else{
                alert('Errore: caricamento dell\'immagine fallito.');
             }
          },
          complete: function(){
            document.getElementById("span_button").innerHTML = "<button type='button' class='btn btn-outline-success' style='margin-bottom: 50px;'' onclick='rilevaRazza()''>Rileva razza</button>";
          }
       });
    }else{
       alert("Scegli un'immagine con cane da analizzare.");
    }
}

function rilevaRazza2() {

      var f = document.getElementById("file").value;
      if (!f) alert("Scegli un'immagine con cane da analizzare!");
      else {

        var formdata = new FormData();

        //Foto
        var foto = document.getElementById("file").files[0];
        formdata.append('foto', foto);

        //ajaxRequest
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200)
            {
              document.getElementById("risultato").innerHTML = this.responseText;
            }
        };
        xmlhttp.open("POST", "server.php", true);
        xmlhttp.setRequestHeader('Content-Type', 'multipart/form-data');
        xmlhttp.send(formdata);
      }
}
