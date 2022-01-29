$(document).ready(function(){
    let input1 = 
        $('<div class="form-floating mb-3" id="input1">'
            + '<input type="text" class="form-control link-document-input" name="link_document" id="floatingInput" placeholder="name@example.com">'
            + '<label for="floatingInput">Link bài viết</label>'
        + '</div>')
    
    let input2 = 
        $('<div class="form-floating mb-3" id="input2">'
            + '<input type="text" class="form-control list-page-input" name="list_pages" id="floatingInput" placeholder="name@example.com">'
            + '<label for="floatingInput">Nhập các trang cần quét từ trang nguồn (cách nhau bởi dấu phẩy - Ví dụ: 1,3,4)</label>'
        + '</div>')

    let input3 = 
        $('<div id="input3">'
            + '<label for="quantity">Từ trang: </label>'
            + '<input type="number" id="quantity" class="start-value-input" name="from" min="1" max="1000" value="1">'
            + '<label for="quantity">Đến trang: </label>'
            + '<input type="number" id="quantity" class="end-value-input" name="to" min="1" max="1000" value="1">'
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
//---------- XÓA DOCUMENT -----------------------------------
    let del_row_document_table

    $('.delete-btn').click(e=>{
        $('.cover_page').css('display', 'flex')
        $('.body-delete-modal').css('display', 'flex')
        $('.body_cover').css('display', 'none')
        $('.deleting-modal').css('display', 'none')

        let docId = $(e.target).attr('data-docid')
        //docId = docId.split('=')[1]

        del_row_document_table = $(e.target)
        while (del_row_document_table.prop("tagName") != 'TR') {
            del_row_document_table = del_row_document_table.parent()
        }

        $('.btn-confirm-delete').attr('data-docid', docId)
    })

    $('.btn-confirm-delete').click(e=>{
        let docId = $(e.target).attr('data-docid')
        console.log(docId)
        $('.cover_page').css('display', 'flex')
        $('.body-delete-modal').css('display', 'none')
        $('.body_cover').css('display', 'none')
        $('.deleting-modal').css('display', 'flex')
        $.ajax({
            url: '/elastic/delete/doc',
            data: {
                docId: docId,
                csrfmiddlewaretoken: csrfToken
            },
            type: 'POST',
        }).done(function(res) {
            if(res['mess']=='successful delete') {
                del_row_document_table.remove()
                console.log('xóa thành công ' + docId)

                $('.cover_page').css('display', 'none')
                $('.body-delete-modal').css('display', 'none')
                $('.body_cover').css('display', 'none')
                $('.deleting-modal').css('display', 'none')
            }
            else{
                $('.cover_page').css('display', 'none')
                $('.body-delete-modal').css('display', 'none')
                $('.body_cover').css('display', 'none')
                $('.deleting-modal').css('display', 'none')
                console.log('xóa thất bại')
            }
        })
    })
    /*------------------ download -----------------*/
    //TÙY CHỌN DOWNLOAD
    $('.download-option').click((e)=>{
        
        let source_name = $(e.target).data('sourcename')
        let link_page = $(e.target).data('linkpage')
        console.log(source_name)
        console.log(link_page)
        $('.scan-button').attr('data-sourceName', source_name)
        $('.scan-button').attr('data-linkPage', link_page)
        $('#modal-source_name').text(source_name)

        $('.body_cover').css('display', 'flex')
        $('.cover_page').css('display', 'flex')
        $('.body-delete-modal').css('display', 'none')
        $('.deleting-modal').css('display', 'none')
    })

    $('.scan-button').click((e)=>{
        
        let source_name = $('#scan-btn').attr('data-sourcename')
        let link_page = $('#scan-btn').attr('data-linkpage')
        console.log('đã lây link page: ', $('#scan-btn').attr('data-linkpage'))

        let request_url = $('#form-option').attr('action')
        let isSave = $('#flexCheckDefault').is(":checked")
        
        //console.log('isSave: ' + isSave)
        console.log('sourcename: ' + source_name)
        console.log('linkpage: ' + link_page)
        //console.log('request_url: ' + request_url)

        if(request_url === 'elastic/insert') {

            let link_document = $('.link-document-input').val()
            $('.link-document-input').val('')
            //console.log(link_document)
            $.ajax({
                url: request_url,
                data: {
                    data: {link_document, link_page, isSave},
                    csrfmiddlewaretoken: csrfToken
                },
                type: 'POST',
            }).done(function(res) {
                //var opened = window.open("");
                //opened.document.write(res);
                console.log(res)
                let id = res['Thread name'].split(' ')[0]
                let name = res['Thread name'].split(' ')[1]
                console.log(id)
                let html = create_block_info_downloading(id, name, source_name)
                $('#list-download-tasking').append(html)
                let intervalId_download = setInterval(()=>{
                    $.ajax({
                        url: 'elastic/progress/download',
                        data: {
                            thread_name: id,
                            csrfmiddlewaretoken: csrfToken
                        },
                        type: 'POST',
                    }).done(function(res) {
                        progress = res['progress']
                        number_of_downloaded = res['downloaded']
                        //console.log(progress)
                        if(number_of_downloaded !== 0){
                            $('#label-document-download-' + id).text('downloading - ' + number_of_downloaded)
                        }
                        $('#progress-download-' + id).text(progress + '%')
                        $('#progress-download-' + id).css('width', progress+'%');
                        if(progress === 100) {
                            console.log('done')
                            clearInterval(intervalId_download)
                            $('#label-document-download-' + id).text('downloaded - ' + number_of_downloaded + ' - done')
                        }
                    })
                },300)
                //-----------------------------------
                let intervalId_save = setInterval(()=>{
                    $.ajax({
                        url: 'elastic/progress/save',
                        data: {
                            thread_name: id,
                            csrfmiddlewaretoken: csrfToken
                        },
                        type: 'POST',
                    }).done(function(res) {
                        progress = res['progress']
                        number_of_saved = res['saved']
                        //console.log(progress)
                        if(number_of_saved !== 0){
                            $('#label-document-save-' + id).text('saving - ' + number_of_saved)
                        }
                        $('#progress-save-' + id).text(progress + '%')
                        $('#progress-save-' + id).css('width', progress+'%');
                        if(progress === 100) {
                            console.log('done')
                            clearInterval(intervalId_save)
                            clearInterval(intervalId_download)
                            $('#label-document-save-' + id).text('saved - ' + number_of_saved + ' - done')
                            setTimeout(()=>{
                                $('#block-btn-control-thread-' + id).css('display', 'none')
                                $('#block-btn-task-info-' + id).css('display', 'flex')
                            },1000)
                        }
                    })
                },300)
            })
        }
        else if (request_url === 'elastic/inserts/range') {
            let from = $('.start-value-input').val()
            let to = $('.end-value-input').val()

            $('.start-value-input').val('1')
            $('.end-value-input').val('1')
            //console.log(from)
            //console.log(to)

            $.ajax({
                url: request_url,
                data: {
                    from: from, 
                    to: to,
                    link_page: link_page,
                    isSave: isSave,
                    csrfmiddlewaretoken: csrfToken
                },
                type: 'POST',
            }).done(function(res) {
                console.log(res)
                let id = res['Thread name'].split(' ')[0]
                let name = res['Thread name'].split(' ')[1]
                console.log(id)
                let html = create_block_info_downloading(id, name, source_name)
                $('#list-download-tasking').append(html)
                let intervalId_download = setInterval(()=>{
                    $.ajax({
                        url: 'elastic/progress/download',
                        data: {
                            thread_name: id,
                            csrfmiddlewaretoken: csrfToken
                        },
                        type: 'POST',
                    }).done(function(res) {
                        progress = res['progress']
                        number_of_downloaded = res['downloaded']
                        //console.log(progress)
                        if(number_of_downloaded !== 0){
                            $('#label-document-download-' + id).text('downloading - ' + number_of_downloaded)
                        }
                        $('#progress-download-' + id).text(progress + '%')
                        $('#progress-download-' + id).css('width', progress+'%');
                        if(progress === 100) {
                            console.log('done')
                            clearInterval(intervalId_download)
                            $('#label-document-download-' + id).text('downloaded - ' + number_of_downloaded + ' - done')
                        }
                    })
                },300)
                //-----------------------------------
                let intervalId_save = setInterval(()=>{
                    $.ajax({
                        url: 'elastic/progress/save',
                        data: {
                            thread_name: id,
                            csrfmiddlewaretoken: csrfToken
                        },
                        type: 'POST',
                    }).done(function(res) {
                        progress = res['progress']
                        number_of_saved = res['saved']
                        //console.log(progress)
                        if(number_of_saved !== 0){
                            $('#label-document-save-' + id).text('saving - ' + number_of_saved)
                        }
                        $('#progress-save-' + id).text(progress + '%')
                        $('#progress-save-' + id).css('width', progress+'%');
                        if(progress === 100) {
                            console.log('done')
                            clearInterval(intervalId_save)
                            clearInterval(intervalId_download)
                            $('#label-document-save-' + id).text('saved - ' + number_of_saved + ' - done')
                            setTimeout(()=>{
                                $('#block-btn-control-thread-' + id).css('display', 'none')
                                $('#block-btn-task-info-' + id).css('display', 'flex')
                            },1000)
                        }
                    })
                },300)
            })
        }
        else if (request_url === 'elastic/inserts/multipage') {
            let list_pages = $('.list-page-input').val()
            console.log('list page: ', list_pages)
            
            $('.list-page-input').val('')
            //console.log(list_pages)
            $.ajax({
                url: request_url,
                data: {
                    link_page: link_page, 
                    list_pages: list_pages,
                    isSave: isSave,
                    csrfmiddlewaretoken: csrfToken
                },
                type: 'POST',
            }).done(function(res) {
                //var opened = window.open("");
                //opened.document.write(res);
                console.log(res)
                let id = res['Thread name'].split(' ')[0]
                let name = res['Thread name'].split(' ')[1]
                console.log(id)
                let html = create_block_info_downloading(id, name, source_name)
                $('#list-download-tasking').append(html)
                let intervalId_download = setInterval(()=>{
                    $.ajax({
                        url: 'elastic/progress/download',
                        data: {
                            thread_name: id,
                            csrfmiddlewaretoken: csrfToken
                        },
                        type: 'POST',
                    }).done(function(res) {
                        progress = res['progress']
                        number_of_downloaded = res['downloaded']
                        //console.log(progress)
                        if(number_of_downloaded !== 0){
                            $('#label-document-download-' + id).text('downloading - ' + number_of_downloaded)
                        }
                        $('#progress-download-' + id).text(progress + '%')
                        $('#progress-download-' + id).css('width', progress+'%');
                        if(progress === 100) {
                            console.log('done')
                            clearInterval(intervalId_download)
                            $('#label-document-download-' + id).text('downloaded - ' + number_of_downloaded + ' - done')
                        }
                    })
                },300)
                //-----------------------------------
                let intervalId_save = setInterval(()=>{
                    $.ajax({
                        url: 'elastic/progress/save',
                        data: {
                            thread_name: id,
                            csrfmiddlewaretoken: csrfToken
                        },
                        type: 'POST',
                    }).done(function(res) {
                        progress = res['progress']
                        number_of_saved = res['saved']
                        //console.log(progress)
                        if(number_of_saved !== 0){
                            $('#label-document-save-' + id).text('saving - ' + number_of_saved)
                        }
                        $('#progress-save-' + id).text(progress + '%')
                        $('#progress-save-' + id).css('width', progress+'%');
                        if(progress === 100) {
                            console.log('done')
                            clearInterval(intervalId_save)
                            clearInterval(intervalId_download)
                            $('#label-document-save-' + id).text('saved - ' + number_of_saved + ' - done')
                            setTimeout(()=>{
                                $('#block-btn-control-thread-' + id).css('display', 'none')
                                $('#block-btn-task-info-' + id).css('display', 'flex')
                            },1000)
                        }
                    })
                },300)
                
            })
        }
        
        $('.body_cover').css('display', 'none')
        $('.cover_page').css('display', 'none')
        $('.body-delete-modal').css('display', 'none')
        $('.deleting-modal').css('display', 'none')
    })

    $('.close-modal').click(()=>{
        $('.body_cover').css('display', 'none')
        $('.cover_page').css('display', 'none')
        $('.body-delete-modal').css('display', 'none')
        $('.deleting-modal').css('display', 'none')
    })



//------------ TÙY CHỌN XÓA NGUỒN ---------------------------
    $('.delete-option').click(e => {
        $('.cover_page').css('display', 'flex')
        $('.body-delete-modal').css('display', 'flex')
        $('.body_cover').css('display', 'none')
        $('.deleting-modal').css('display', 'none')

        let source_name = $(e.target).data('sourcename')
        let link_page = $(e.target).data('linkpage')
        console.log(source_name)
        console.log(link_page)

        del_row_source_table = $(e.target)
        while (del_row_source_table.prop("tagName") != 'TR') {
            del_row_source_table = del_row_source_table.parent()
        }

        $('.modal-delete-button').attr('data-sourceName', source_name)
        $('.modal-delete-button').attr('data-linkpage', link_page)
    })

    //---------------- MODAL XÁC NHẬN XÓA NGUỒN ----------------
    let del_row_source_table
    
    $('.close-delete-modal').click(e => {
        $('.body_cover').css('display', 'none')
        $('.cover_page').css('display', 'none')
        $('.body-delete-modal').css('display', 'none')
        $('.deleting-modal').css('display', 'none')
    })

    $('.modal-delete-button').click(e=>{
        $('.body_cover').css('display', 'none')
        $('.cover_page').css('display', 'flex')
        $('.body-delete-modal').css('display', 'none')
        $('.deleting-modal').css('display', 'flex')

        let source_name = $(e.target).data('sourcename')
        let link_page = $(e.target).data('linkpage')
        console.log(source_name)
        console.log(link_page)

        $.ajax({
            url: 'elastic/source/delete',
            data: {
                link_page: link_page,
                source_name: source_name,
                csrfmiddlewaretoken: csrfToken
            },
            type: 'POST',
        }).done(function(res) {
            //var opened = window.open("");
            //opened.document.write(res);
            console.log(res)
            if(res['mess']=='successful delete') {
                $('.body_cover').css('display', 'none')
                $('.cover_page').css('display', 'none')
                $('.body-delete-modal').css('display', 'none')
                $('.deleting-modal').css('display', 'none')
                del_row_source_table.remove()
            }
        })
    })

    //----------------------xem ket qua tai ve ----------------------------
    $(document).on('click', '.btn-show-detail-download', e=>{
        let thread_name = $(e.target).attr('thread')
        console.log('show detail ', thread_name)
    })

    $(document).on('click', '.btn-close-task-info', e=>{
        let thread_name = $(e.target).attr('thread')
        console.log('close task block ', thread_name)
        $('#' + thread_name).remove()
    })

    //------------ PAUSE - RESUME - STOP THREAD -----------------
    // pause
    $(document).on('click', '.btn-pause-thread', e=>{
        let thread_name = $(e.target).attr('thread')
        console.log('show detail btn pause: ', thread_name)
        $.ajax({
            url: 'elastic/thread/pause',
            data: {
                thread_name: thread_name,
                csrfmiddlewaretoken: csrfToken
            },
            type: 'POST',
        }).done(function(res) {
            list_thread = res['Thread name']
            console.log(list_thread)
            $('#progress-download-' + thread_name).addClass('bg-warning')
            $('#progress-save-' + thread_name).addClass('bg-warning')
        })
    })
    // resume
    $(document).on('click', '.btn-resume-thread', e=>{
        let thread_name = $(e.target).attr('thread')
        console.log('show detail btn resume: ', thread_name)
        $.ajax({
            url: 'elastic/thread/resume',
            data: {
                thread_name: thread_name,
                csrfmiddlewaretoken: csrfToken
            },
            type: 'POST',
        }).done(function(res) {
            list_thread = res['Thread name']
            console.log(list_thread)
            $('#progress-download-' + thread_name).removeClass('bg-warning')
            $('#progress-save-' + thread_name).removeClass('bg-warning')
        })
    })
    //stop
    $(document).on('click', '.btn-stop-thread', e=>{
        let thread_name = $(e.target).attr('thread')
        console.log('show detail btn stop: ', thread_name)
        $.ajax({
            url: 'elastic/thread/stop',
            data: {
                thread_name: thread_name,
                csrfmiddlewaretoken: csrfToken
            },
            type: 'POST',
        }).done(function(res) {
            list_thread = res['Thread name']
            console.log(list_thread)
            $('#progress-download-' + thread_name).addClass('bg-danger')
            $('#progress-save-' + thread_name).addClass('bg-danger')
            $('#block-btn-control-thread-' + thread_name).css('display', 'none')
            $('#block-btn-task-info-' + thread_name).css('display', 'flex')
        })
    })


    function create_block_info_downloading(id, name, source_name) {
        let html = '<li class="list-group-item list-group-item-tasking" id="' + id + '">'
        +    '<div class="block-tasking">'
        +        '<div class="source-name-tasking">'
        +            '<h6>' + source_name +'</h6>'
        +        '</div>'
        +       '<div class="progress-tasking">'
        +          '<label id="label-document-download-' + id + '">downloading:</label>'
        +         '<div class="progress">'
        +            '<div class="progress-bar" role="progressbar" style="width: 0%;"'
        +               'aria-valuenow="25" aria-valuemin="0" aria-valuemax="100" id="progress-download-' + id + '">'
        +                    '0%'
        +                '</div>'
        +            '</div>'
        +            '<label id="label-document-save-' + id + '">saving:</label>'
        +            '<div class="progress">'
        +                '<div class="progress-bar" role="progressbar" style="width: 0%;"'
        +                    'aria-valuenow="25" aria-valuemin="0" aria-valuemax="100" id="progress-save-' + id + '">'
        +                    '0%'
        +                '</div>'
        +            '</div>'
        +        '</div>'
        +    '</div>'

        +    '<div class="block-btn-control-thread" id="block-btn-control-thread-' + id +'" style="display: flex; justify-content: space-between; margin-top: 15px;">'
        +        '<div class="btn btn-warning btn-pause-thread" id="btn-pause-thread-'+ id +'" thread="'+ id +'" style="display: flex; width: 80px; justify-content: center;">'
        +            '<i class="far fa-pause-circle" thread="'+ id +'"></i>'
        +            '<div style="font-size: 11px; margin-left: 3px;" thread="'+ id +'">Pause</div>'
        +        '</div>'

        +        '<div class="btn btn-primary btn-resume-thread" id="btn-resume-thread-'+ id +'" thread="'+ id +'" style="display: flex; width: 80px; justify-content: center;">'
        +            '<i class="far fa-play-circle" thread="'+ id +'"></i>'
        +            '<div style="font-size: 11px; margin-left: 3px;" thread="'+ id +'">Resume</div>'
        +        '</div>'

        +        '<div class="btn btn-danger btn-stop-thread" id="btn-stop-thread-'+ id +'" thread="'+ id +'" style="display: flex; width: 80px; justify-content: center;">'
        +            '<i class="far fa-stop-circle" thread="'+ id +'"></i>'
        +            '<div style="font-size: 11px; margin-left: 3px;" thread="'+ id +'">Stop</div>'
        +        '</div>'
        +    '</div>'

        +    '<div class="block-button-result-task" id="block-btn-task-info-' + id +'">'
        +       '<a href="elastic/result/list_document?thread_name=' + id + '" target="_blank">'
        +           '<button type="button" class="btn btn-success btn-result-task-item btn-show-detail-download" thread="'+ id +'" title="Xem kết quả" style="display: flex;">'
        +               '<i class="fas fa-poll-h" style="margin-right: 6px;" thread="'+ id +'"></i>'
        +               '<div style="font-size: 11px;" thread="'+ id +'">Detail</div>'
        +           '</button>'
        +       '</a>'
        +        '<button type="button" class="btn btn-danger btn-result-task-item btn-close-task-info" thread="'+ id +'" title="Đóng" style="display: flex;">'
        +            '<i class="far fa-times-circle" style="margin-right: 6px;" thread="'+ id +'"></i>'
        +            '<div style="font-size: 11px;" thread="'+ id +'">Close</div>'
        +        '</button>'
        +    '</div>'    
        + '</li>'
        return html
    }

});