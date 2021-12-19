$(document).ready(function(){
    let input1 = 
        $('<div class="form-floating mb-3" id="input1">'
            + '<input type="text" class="form-control" name="link_document" id="floatingInput" placeholder="name@example.com">'
            + '<label for="floatingInput">Link bài viết</label>'
        + '</div>')
    
    let input2 = 
        $('<div class="form-floating mb-3" id="input2">'
            + '<input type="text" class="form-control" name="list_pages" id="floatingInput" placeholder="name@example.com">'
            + '<label for="floatingInput">Nhập các trang cần quét từ trang nguồn (cách nhau bởi dấu phẩy - Ví dụ: 1,3,4)</label>'
        + '</div>')

    let input3 = 
        $('<div id="input3">'
            + '<label for="quantity">Từ trang: </label>'
            + '<input type="number" id="quantity" name="from" min="1" max="1000" value="1">'
            + '<label for="quantity">Đến trang: </label>'
            + '<input type="number" id="quantity" name="to" min="1" max="1000" value="1">'
        + '</div>')

    app = 'elastic'   
    $('.option1').click(()=>{
        path = ''
        method = $('input[name="method"]:checked').val();
        //console.log(method)
        path += app + method 
        console.log(path)
        $('#form-option').attr('action', path)
        $('#special_input').remove()
        if(input2){
            input2.remove()
        }
        if(input3){
            input3.remove()
        }
        $('#checkBoxSave').before(input1)
    })

    $('.option2').click(()=>{
        path = ''
        method = $('input[name="method"]:checked').val();
        //console.log(method)
        path += app + method
        console.log(path)
        $('#form-option').attr('action', path)
        $('#special_input').remove()
        if(input1){
            input1.remove()
        }
        if(input3){
            input3.remove()
        }
        $('#checkBoxSave').before(input2)
    })

    $('.option3').click(()=>{
        path=''
        method = $('input[name="method"]:checked').val();
        //console.log(method)
        path += app + method
        console.log(path)
        $('#form-option').attr('action', path)
        $('#special_input').remove()
        if(input1){
            input1.remove()
        }
        if(input2){
            input2.remove()
        }
        
        $('#checkBoxSave').before(input3)
    })

    $('select').on('change', function (e) {
        var optionSelected = $("option:selected", this);
        var valueSelected = this.value;
        console.log(valueSelected)
        if(valueSelected === '1'){
            app = 'elastic'
            path = source + $('input[name="method"]:checked').val();
            $('#form-option').attr('action', path)
            console.log('da doi: ', $('#form-option').attr('action'))
        }
        else if(valueSelected === '2'){
            app = 'elastic'
            path = source + $('input[name="method"]:checked').val();
            $('#form-option').attr('action', path)
            console.log('da doi: ', $('#form-option').attr('action'))
        }
        else if(valueSelected === '3'){
            app = 'elastic'
            path = source + $('input[name="method"]:checked').val();
            $('#form-option').attr('action', path)
            console.log('da doi: ', $('#form-option').attr('action'))
        }
    });



    //###############################################
    // SEARCH - FEARURE
    //###############################################
    console.log('OK da nap')
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrfToken = getCookie('csrftoken');
    console.log('in ra:')
    console.log(csrfToken)

    function create_element(en, vi){
        element = '<div class="row unit-corpus"><div class="col"><h6>English:</h6><p>'
        + en
        + '</p></div><div class="col"><h6>Vietnamese:</h6><p>'
        +  vi
        + '</p></div></div>'
        return element
    }

    $('#search-btn').click(function(){
        let input = $('#search-input').val()
        console.log('Đã bấm')
        if(input != ''){
            $.ajax({
                url: '/elastic/search',
                data: {
                    data: input,
                    csrfmiddlewaretoken: csrfToken
                },
                type: 'POST',
            }).done(function(res) {
                $('.unit-corpus').remove()
                for (let i = 0; i < res.result.length; i++) {

                    console.log(res.result[i][0])
                    console.log(res.result[i][1])
                    $('#main-contain').append(create_element(res.result[i][0], res.result[i][1]))
                }
            })
        }
    })
});