function log(message) {
    $("#log").html(message);
}
var loader_pic = '<br><img height="42" width="42" src="' + LOADER_GIF + '">';

function get_download_links(lnks){
    var rv = 'Here are the download alternatives:<ul>';
    for(var k in lnks) {
        rv += '<li><a href="' + lnks[k].url + '">' + k + ' (' +  lnks[k].size + ')</a></li>';
    }
    rv += '</ul>';
    return rv;
}

function upload(file, token, md5) {
    function do_poll() {
        $.post(QUEUE_LENGTH_URL, {csrfmiddlewaretoken: token, md5: md5}, function (data) {
            queue_length.html(data);
        });
        if(!stop_polling)
            setTimeout(do_poll, 30000);
    }
    var formdata = new FormData();

    if (file) {
        log('Uploading file. ' + loader_pic);
        formdata.append('file', file);
    }
    else {
        log('Converting file on the server. Download link will appear here when it is finished. ' +
            'If you wish not to wait, you may also try again later. ' +
            'Work queue length: <span id="queue_length"> - not known - </span>.' +
            loader_pic);
        do_poll();
    }

    var filename = $('#file')[0].files[0].name;
    formdata.append('csrfmiddlewaretoken', token);
    formdata.append('md5', md5);
    formdata.append('filename', filename);

    var queue_length = $("#queue_length");
    var stop_polling = false;



    $.ajax({
        type: 'POST', url: UPLOAD_URL, data: formdata, processData: false, contentType: false,
        success: function (data) {
            if (data.status==1) {
                log('Now you can start downloading. ' + get_download_links(data.download_links));
                stop_polling = true;
            }
            else if (data.status==2) {
                log('Upload finished');
                return upload(false, token, md5);
            }
            else
                log("Conversion error has occurred. The maintainer will be informed, " +
                    "and he has now enough data to improve the conversion script for the future use.");
            $('#file').removeAttr('disabled');
        },
        error: function() {
            log('Connection was lost, please try again!');
            stop_polling = true;
        }
    });

}

function fileready(md5) {
    log('MD5 sum checking ready. Wait a moment... ' + loader_pic);
    var token = $('input[name=csrfmiddlewaretoken]').val();
    var fileinput = $('#file');
    var filename = fileinput[0].files[0].name;
    $.post(IS_FILE_CACHED_URL, {csrfmiddlewaretoken: token, md5: md5, filename: filename}, function (result) {
        if (result.status) {
            if (result.cached == 1) {
                if (result.status == 1)
                    log('Converted file was found cached on the server, you may start downloading immedediately. ' +
                        get_download_links(result.download_links));
                else if (result.status == 2) {
                    upload(false, token, md5);
                }
            }
            else {
                var file = $('#file')[0].files[0];
                upload(file, token, md5);
            }
        }
        else
            log("There is server-side error that occurs for this file, I'm sorry. Try again later. ");
        fileinput.removeAttr('disabled');

    }).fail(function() {
        log('Connection was lost, please try again!');
    });
}

$(document).ready(function () {
    var fileinput = $('#file');
    fileinput.change(function () {
        var filename = fileinput[0].files[0].name;
        var blobSlice = File.prototype.slice || File.prototype.mozSlice || File.prototype.webkitSlice,
            file = this.files[0],
            chunkSize = 2097152,                               // read in chunks of 2MB
            chunks = Math.ceil(file.size / chunkSize),
            currentChunk = 0,
            spark = new SparkMD5.ArrayBuffer(),
            frOnload = function (e) {
                console.log("read chunk nr", currentChunk + 1, "of", chunks);
                spark.append(e.target.result);                 // append array buffer
                currentChunk++;

                if (currentChunk < chunks) {
                    loadNext();
                }
                else {
                    fileready(spark.end());
                }
            },
            frOnerror = function () {
                log('Oops! Something went wrong while checking MD5 sum (browser problem, try another browser?)!');
            };

        function loadNext() {
            var fileReader = new FileReader();
            fileReader.onload = frOnload;
            fileReader.onerror = frOnerror;

            var start = currentChunk * chunkSize,
                end = ((start + chunkSize) >= file.size) ? file.size : start + chunkSize;

            fileReader.readAsArrayBuffer(blobSlice.call(file, start, end));
        }

        fileinput.attr('disabled', "1");
        log('Checking MD5 sum, please wait...' + loader_pic);
        loadNext();
    });

});
