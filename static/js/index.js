const fileUploader = document.querySelector("#file-uploader");
const contentBox = document.querySelector(".content-box");
const comment = document.querySelector(".comment");
const btn = document.querySelector(".btn");


let imgData = null;
const reader = new FileReader();


fileUploader.onchange = (e) => {
  reader.readAsDataURL(e.target.files[0]);
  reader.onload = (evt) => {
    imgData = evt.target.result;
  }
}


btn.addEventListener("click", function(){
  fetch(`/uploadData`, {
    method: "POST",
    body: JSON.stringify({
      comment: comment.value,
      image: imgData
    }),
    headers: {
      "Content-type": "application/json"
    },
  })
  .then((response) => response.json())
  .then((data) => {
    if(data.data){
      // history.go(0);
      window.location = "/";
    }
  })
  // }

});

fetch(`/showData`, {
    method: "GET",
  })
  .then((response) => response.json())
  .then((data) => {

    let html = "";
    data.data.forEach(comment => {
      let txt = `
        <h5 class="content">${comment.message}</h5>
        <img src="${comment.url}" alt="">
        <hr>
      `
      html += txt
    }); 

    contentBox.insertAdjacentHTML("beforeEnd", html);
  })