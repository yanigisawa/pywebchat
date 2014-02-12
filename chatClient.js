var ChatClient = function(messageLog, userNameField, messageField, userLog) { 
    var _messageLog = messageLog;
    var _userNameField = userNameField;
    var _messageField = messageField;
    var _userLog = userLog;

    this.IdleInterval = 60000;
    this.Active = null;
    this.TitleToggleInterval = null;
    this.TotalMessageCount = 0;

    this.ToggleTitle = function () {
        var text = document.title;
        if (text == "New Message") { text = "Look Here"; }
        else { text = "New Message" }

        document.title = text;
    };

    var formatTime = function(d) {
        var a_p = "AM";
        d = new Date(d + "Z");
        var curr_hour = d.getHours();
        if (curr_hour >= 12) {
            a_p = "PM";
            curr_hour = curr_hour - 12;
        }

        if (curr_hour == 0) { curr_hour = 12; }

        var curr_min = d.getMinutes() + "";
        curr_hour = curr_hour + "";

        if (curr_min.length == 1) { curr_min = "0" + curr_min; }

        if (curr_hour.legth == 1) { curr_hour = "0" + curr_hour; }

        return curr_hour + ":" + curr_min + " " + a_p;
    };

    this.scrollToBottom = function () {
        height = _messageLog.prop("scrollHeight");
        _messageLog.animate( { scrollTop: height }, 1000); 
    };

    this.PrintMessages = function(messageArr) {
        var messageCount = messageArr.length;
        var messages = [];
        for(var i = 0; i < messageCount; i++) {
            messages.push("<span class='metaData'>", messageArr[i].user, " - ");
            messages.push(formatTime(messageArr[i].date), "</span><span class='message'>");
            messages.push(": ", messageArr[i].message, "</span><br/>");
        }
        _messageLog.html(messages.join(""));
        this.scrollToBottom();
    };

    this.printUsers = function(userArray) {
        var userCount = userArray.length;
        var userStringArr = [];

        for (var i = 0; i < userCount; i++) {
            if (userArray[i].active) {
                userStringArr.push("<img src='img/online.png' height='16px' width='16px' />");
            } else {
                userStringArr.push("<img src='img/idle.png' height='16px' width='16px' />");
            }
            userStringArr.push("<span class='user'>", userArray[i].name, "</span></br>");
        }
        _userLog.html(userStringArr.join(""));
    };

    this.postMessage = function () {

        if(!$.trim(_userNameField.val()).length) {
            alert("Please enter a user name to post as.");
            return;
        }

        if(!$.trim(_messageField.val()).length) {
            return;
        }

        var msg = _messageField.val();
        _messageField.val("");
        _messageField.prop("readonly", true);
        _messageField.addClass("posting");

        $.ajax({
            type: "PUT",
            url: "newmessage",
            dataType: "json",
            data: { 
                name: _userNameField.val(), 
                message: msg,
            },
            error: function() { 
                $("#messageLog").append("### - Failed to post message - ###</br>"); 
            },
            complete: function() {
                _messageField.prop("readonly", false);
                _messageField.removeClass("posting");
            }
        });
    };

    this.readMessages = function (callBack) {
        var that = this;
        var success = function(result) {
            if (result.success && result.data !== undefined && result.data.messages !== undefined) {
                that.PrintMessages(result.data.messages);
                that.printUsers(result.data.users);
                that.TotalMessageCount = result.data.messages.length;
            }
        };

        $.ajax({
            type: "POST",
            url: "/readmessages",
            dataType: "json",
            success: success,
            error: function() { 
                $("#messageLog").append("### - Failed to read messages from server - ###</br>"); 
            },
            complete: function () {
                if (callBack !== undefined) { callBack(); }
            }
        });
    };
};

var chatClient = new ChatClient($("#messageLog"), $("#userName"), $("#message"), $("#users"));

ChatClient.poll = function (){
    $.ajax({ 
        url: "/poll", 
        type: "POST",
        data: {
            poll: true,
        },
        success: function(result){
            if (result.success && result.data !== undefined) { 
                messages = result.data.messages;
                messageCount = messages.length;
                chatClient.printUsers(result.data.users);
                var shouldToggleTitleBar = messageCount > chatClient.TotalMessageCount &&
                    messages[messageCount - 1].user != $("#userName").val();
                if (shouldToggleTitleBar) {
                    clearInterval(chatClient.TitleToggleInterval);
                    chatClient.TitleToggleInterval = setInterval(chatClient.ToggleTitle, 1000);
                }

                if (messageCount > chatClient.TotalMessageCount) {
                    chatClient.PrintMessages(messages);
                }
                chatClient.TotalMessageCount = messageCount;
            }
        }, 
        dataType: "json", 
        complete: ChatClient.poll, 
        timeout: 60000 
    });
};

ChatClient.SendActivity = function(isActive) { 
    if (!$.trim($("#userName").val())) {
        return;
    }

    chatClient.Active = isActive;

    $.ajax({
        type: "PUT",
        url: "/useractivity",
        dataType: "json",
        data: { 
            name: $("#userName").val(), 
            activity: true,
            active: chatClient.Active,
        },
        error: function() { 
            $("#messageLog").append("### - Failed to send user activity - ###</br>"); 
        }
    });
}

ChatClient.SetUserIdle = function() {
    var active_tmp = chatClient.Active;
    clearTimeout(ChatClient.ActivityTimer);
    ChatClient.ActivityTimer = setTimeout(ChatClient.SetUserIdle, 120000);
    ChatClient.SendActivity(false);
};

ChatClient.ActivityTimer = setTimeout(ChatClient.SetUserIdle, chatClient.IdleInterval);

ChatClient.SetUserActive = function() {
    clearTimeout(ChatClient.ActivityTimer);
    ChatClient.ActivityTimer = setTimeout(ChatClient.SetUserIdle, chatClient.IdleInterval);
    if (!$("#userName").is(":focus") && !chatClient.Active) { ChatClient.SendActivity(true); }
};


$(document).bind("mousemove", ChatClient.SetUserActive);
$(document).bind("keypress", ChatClient.SetUserActive);

$(document).ready(function() {
    $("#newMessage").click(function () {
        if($.trim($("#message").val()).length) {
            chatClient.postMessage();
        }
    });

    $("#refresh").click(function () {
        chatClient.TotalMessageCount = 0;
        $("#messageLog").html("");
        $("#users").html("");
        chatClient.readMessages();
    });

    $("#message").keypress(function (e) {
        if (e.keyCode == 13 && $.trim($("#message").val()).length) {
            chatClient.postMessage();
        }
    });

    $("#message").focus(function() { 
        clearInterval(chatClient.TitleToggleInterval); 
        document.title = "Web Chat";
    } );

    chatClient.readMessages(ChatClient.poll);
});



