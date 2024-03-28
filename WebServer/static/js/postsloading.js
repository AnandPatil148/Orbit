function displayPosts(data)
{
    var card = document.createElement("div");
    card.className = "card";
    //card.style.width="30rem";
    
    //Card Header of the post
    var header = document.createElement("div");
    header.className = "card-header";
    //header.style.height = "";

    var pfp_img = document.createElement("img");
    //pfp_img.src= data["pfp"];
    pfp_img.src= "/static/images/Nubs_icon.png";
    pfp_img.alt = "Profile Picture";
    pfp_img.style.height = "10%";
    pfp_img.style.width = "10%";
    header.appendChild(pfp_img); // add profile picture to header 
    
    
    var userName = document.createElement("p");
    userName.textContent = data.Name;
    userName.style.display = 'inline';
    userName.style.marginLeft ="10px";
    userName.style.fontWeight = "bold";
    userName.style.color = "#6c757d";
    userName.style.verticalAlign = "baseline";
    header.appendChild(userName);
    
    //header.appendChild(document.createTextNode(data.Name));
    card.appendChild(header);
    
    //Card Body 
    var body = document.createElement("div");
    body.className ="card-body";

    // Card title
    var title = document.createElement("h5");
    title.className="card-title";
    title.innerText="";//Add title here later
    body.appendChild(title);

    /*
    // Check if Any Attachments like images or videos
    if (data.Attachment) {
        var imgDiv = document.createElement('div');
        imgDiv.id='imagePost'
        
        var image = new Image();
        image.onload = function() {
            imgDiv.appendChild(this);
            body.appendChild(imgDiv);
        };
        image.src = '/post/' + data.ID + '/attachment';
        image.style.maxHeight = "400px" ;
        image.style.objectFit = "contain";
        image.alt = "Image Post";

        var vidDiv = document.createElement('div');
        vidDiv.id= 'videoPost';
        var video = document.createElement('iframe');
        video.width = "320";
        video.height = "240;
        */
    // Card Message
    var message = document.createElement("p");
    message.className="card-text";
    message.innerText=data.Message;
    body.appendChild(message);

    // View Comments Box
    var comment = document.createElement("a");
    comment.href="#";
    comment.className="";
    //comment_btn.setAttribute('onclick','displayComments(\'' + data['ID'] + '\')');
    comment.innerText="View Comments (Under Dev)";
    body.appendChild(comment);
    
    card.appendChild(body);

    // Footed for Date and Time
    var footer = document.createElement("div");
    footer.className = "card-footer text-muted";
    footer.innerHTML ="Time posted: "+ new Date(data.TimeStamp).toLocaleString(); 
    card.appendChild(footer);

    // Append to body
    document.getElementById("posts-display").appendChild(card);

}