const BASE_URL = "http://127.0.0.1:5000"


$('.like').click(async function(evt){
    evt.preventDefault();

    let msg_id = evt.target.id;
    console.log(msg_id)

    res = await axios.post(`${BASE_URL}/users/add_like/${msg_id}`);


    if (res.data == "liked") {
        $(`#${msg_id}`).children().remove()
        $(`#${msg_id}`).append('<i style="pointer-events: none" class="far fa-star fa-sm"<i>')
        $(`#${msg_id}`).removeClass('btn-secondary').addClass('btn-warning btn-sm')
    } else if (res.data === "unliked") {
        $(`#${msg_id}`).children().remove()
        $(`#${msg_id}`).append('<i style="pointer-events: none" class="fa fa-thumbs-up"<i>')
        $(`#${msg_id}`).removeClass('btn-warning').addClass('btn-secondary')
    }
    return "done"
    
})


$('#add-message').click(async function(evt){
    evt.preventDefault();
    

    let text = $('#text').val()
    let $alert = $('#alert')
    $alert.empty()
    
    
    if(text.length == 0){
        $alert.append("<p>Please enter a message</p");
    } else if (text.length > 140) {
        $alert.append("<p>Too many characters</p>")
    } else {
        res = await axios.post(`${BASE_URL}/messages/new`, {"message": `${text}`})
        console.log(res)
    }
})