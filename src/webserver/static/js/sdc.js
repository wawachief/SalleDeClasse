$.extend($.fn.dataTable.defaults, {
    responsive: true
});
$(document).ready(function () {
    var socket = io();
    socket.on('connect', function () {
        socket.emit('confirm_connect', {data: 'I\'m connected!'});
        console.log("connected");
    });
    socket.on('select_student', function (msg) {
        console.log("Received select_student event :  id: " + msg.id + " selected:" + msg.selected);
        if ((msg.selected && !$("#" + msg.id).hasClass("selected")) || (!msg.selected && $("#" + msg.id).hasClass("selected"))){
            $("#" + msg.id).toggleClass("selected");
        }
    });
    var table = $('#students-table').DataTable({
        paging: false,
        fixedHeader: {
            header: false,
            footer: false
        }
    });

    $('#students-table tbody').on('click', 'tr', function () {
        $(this).toggleClass('selected');
        const id = $(this).attr('id');
        const selected = $(this).hasClass("selected");
        $.ajax({
            url: '/api/student?id=' + id + "&selected=" + selected,
            success: function (data) {
            }
        });
        return false;
    });

    $('#button').click(function () {
        socket.emit('random_selection');
    });
});
