var ChatClient = function(messageLog, userNameField, messageField, userLog) { 
    var _messageLog = messageLog;
    var _userNameField = userNameField;
    var _messageField = messageField;
    var _userLog = userLog;

    this.IdleInterval = 60000;
    this.Active = null;
    this.TitleToggleInterval = null;
    this.TotalMessageCount = 0;
    this.ContinuePolling = true;

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
            var cssClass = "generalUserStyle";
            if (messageArr[i].user != _userNameField.val()) { 
                cssClass = "generalUserStyle userStyle";
            }
            messageArr[i].cssClass = cssClass;
            messageArr[i].date = formatTime(messageArr[i].date);
        }

        var source = $("#message-template").html();
        var template = Handlebars.compile(source);

        var html = template({ messages: messageArr});
        _messageLog.html(html);
        this.scrollToBottom();
    };

    this.printUsers = function(userArray) {
        var userCount = userArray.length;
        var userStringArr = [];

        for (var i = 0; i < userCount; i++) {
            var image = "idle";
            if (userArray[i].active) {
                image = "online";
            }
            userArray[i].image = image;
        }
        
        var source = $("#user-template").html();
        var template = Handlebars.compile(source);

        _userLog.html(template({ users: userArray }));
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
            url: config.room + "/newmessage",
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
            url: config.room + "/readmessages",
            dataType: "json",
            success: success,
            error: function() { 
                $("#messageLog").append("### - Failed to read messages from server - ###</br>"); 
            },
            complete: function () {
                if (callBack !== undefined || callBack != null) { callBack(); }
            }
        });
    };
};

var chatClient = new ChatClient($("#messageLog"), $("#userName"), $("#message"), $("#users"));

ChatClient.poll = function (){
    $.ajax({ 
        url: config.room + "/poll", 
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
                    messages[messageCount - 1].user != $("#userName").val() && 
                    !$("#message").is(":focus");
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
        complete: function() {
            if (chatClient.ContinuePolling) {
                ChatClient.poll();
            }
        }, 
        timeout: 40000 
    });
};

ChatClient.SendActivity = function(isActive) { 
    if (!$.trim($("#userName").val())) {
        return;
    }

    chatClient.Active = isActive;

    $.ajax({
        type: "PUT",
        url: config.room + "/useractivity",
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

ChatClient.StopPolling = function() {
    $("#messageLog").html("<b>Chat halted due to inactivity. Click Refresh to resume chat.</b>");
    chatClient.ContinuePolling = false;
    clearTimeout(ChatClient.ActivityTimer);
    clearTimeout(ChatClient.StopPollingTimer);
}

ChatClient.SetUserIdle = function() {
    var active_tmp = chatClient.Active;
    clearTimeout(ChatClient.ActivityTimer);
    ChatClient.ActivityTimer = setTimeout(ChatClient.SetUserIdle, 120000);
    ChatClient.SendActivity(false);
    clearTimeout(ChatClient.StopPollingTimer);
    var ninetyMinutes = 240 * 60 * 1000;
    ChatClient.StopPollingTimer = setTimeout(ChatClient.StopPolling, ninetyMinutes); 
};

ChatClient.ActivityTimer = setTimeout(ChatClient.SetUserIdle, chatClient.IdleInterval);

ChatClient.SetUserActive = function() {
    clearTimeout(ChatClient.ActivityTimer);
    clearTimeout(ChatClient.StopPollingTimer);
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

    var refresh = function () {
        chatClient.TotalMessageCount = 0;
        $("#messageLog").html("");
        $("#users").html("");
        var callBack = null;
        if (!chatClient.ContinuePolling) {
            chatClient.ContinuePolling = true;
            callBack = ChatClient.poll;
        }
        $("#console").append(callBack);
        chatClient.readMessages(callBack);
    };
    $("#refresh").click(refresh);
    Mousetrap.bind('ctrl+r', refresh);

    $("#message").keypress(function (e) {
        if (e.keyCode == 13 && $.trim($("#message").val()).length) {
            chatClient.postMessage();
        }
    });

    $("#message").focus(function() { 
        clearInterval(chatClient.TitleToggleInterval); 
        document.title = config.room + " - Web Chat";
    } );

    chatClient.readMessages(ChatClient.poll);
});



