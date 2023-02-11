function followUser(user) {
    var server_data = [
        { "User": user }
    ];
    $.ajax({
        type: "POST",
        url: "/follow_user",
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: 'json',
        success: function(result) {
            alert(result)
        }
    });
}