var crop_max_width = 300;
var crop_max_height = 300;
var jcrop_api;
var canvas;
var context;
var image;

var prefsize;

function loadImage(input) {
    if (input.files && input.files[0]) {
        if (input.files[0].type.search(/image\/(jpeg|png|jpg)/) === -1) {
            document.getElementById('image').value = "";
            return;
        }
        var reader = new FileReader();
        canvas = null;
        reader.onload = function(e) {
            image = new Image();
            image.onload = validateImage;
            image.src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function validateImage() {
    if (canvas != null) {
        image = new Image();
        image.onload = restartJcrop;
        image.src = canvas.toDataURL('image/jpeg');
    } else restartJcrop();
}

function restartJcrop() {
    if (image.naturalHeight < 256 || image.naturalWidth < 256) {
        document.getElementById('image').value = "";
        return;
    }
    if (jcrop_api != null) {
        jcrop_api.destroy();
    }
    $("#views").empty();
    $("#views").append("<canvas id=\"canvas\">");
    $("#views").append("<input type=\"button\" id=\"cropbutton\" value=\"Crop\" class=\"btn\" onclick=\"applyCrop()\">");
    canvas = $("#canvas")[0];
    context = canvas.getContext("2d");
    canvas.width = image.width;
    canvas.height = image.height;
    context.drawImage(image, 0, 0);
    $("#canvas").Jcrop({
        onSelect: selectcanvas,
        onRelease: clearcanvas,
        aspectRatio: 1,
        minSize: [256, 256],
        maxSize: [1024, 1024],
        boxWidth: crop_max_width,
        boxHeight: crop_max_height
    }, function() {
        jcrop_api = this;
    });
    clearcanvas();
}

function clearcanvas() {
    prefsize = {
        x: 0,
        y: 0,
        w: canvas.width,
        h: canvas.height
    };
}

function selectcanvas(coords) {
    prefsize = {
        x: Math.round(coords.x),
        y: Math.round(coords.y),
        w: Math.round(coords.w),
        h: Math.round(coords.h)
    };
}

function applyCrop() {
    canvas.width = prefsize.w;
    canvas.height = prefsize.h;
    context.drawImage(image, prefsize.x, prefsize.y, prefsize.w, prefsize.h, 0, 0, canvas.width, canvas.height);
    document.getElementById('hidden_img').value = canvas.toDataURL('image/jpeg');
    validateImage();
}
