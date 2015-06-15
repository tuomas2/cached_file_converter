function log(message) {
    $("#log").html(message);
}
var loader_pic = '<br><img height="42" width="42" src="' + LOADER_GIF + '">';
function upload(file, token, md5) {
    if (file)
        log('Uploading and converting file. Please wait! It will finish eventually, <br>' +
            'but may take some time. Download link will appear here when it is finished. ' + loader_pic);
    else
        log('Converting file. Cached version of file you were about to upload was found on server, but it is not yet converted. <br>' +
            'Please wait! It will finish eventually, but may take some time. <br>' +
            'Download link will appear here when it is finished. ' +
            loader_pic);
    var formdata = new FormData();
    if (file) {
        formdata.append('file', file);
    }
    var filename = $('#file')[0].files[0].name;
    formdata.append('csrfmiddlewaretoken', token);
    formdata.append('md5', md5);
    formdata.append('filename', filename);

    $.ajax({
        type: 'POST', url: UPLOAD_URL, data: formdata, processData: false, contentType: false,
        success: function (data) {
            if (data.status)
                log('Now you can start downloading. <br>Here is <a href="' + data.download_link +
                    '">link to processed file</a>.');
            else
                log("Conversion error has occurred. The maintainer will be informed, " +
                    "and he has now enough data to improve the conversion script for the future use.");
            $('#file').removeAttr('disabled');
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
                        '<br>Here is <a href="' + result.download_link + '">link to processed file</a>.');
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