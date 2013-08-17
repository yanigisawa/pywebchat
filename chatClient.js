var ChatClient =  { 
    totalMessageCount: 0,
    titleToggleInterval: 0,
    isPostingMessage: false,

    formatTime: function(d) {
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
    },

    scrollToBottom: function () {
        //height = $("#messageLog")[0].scrollHeight;
        height = $("#messageLog").prop("scrollHeight");
        $('#messageLog').animate( { scrollTop: height }, 1000); 
    },

    printMessages: function(messageArr) {
        var messageCount = messageArr.length;
        var messages = "";
        for(var i = 0; i < messageCount; i++) {
            if (i >= ChatClient.totalMessageCount) {
                messages += "<span class='metaData'>";
                messages += messageArr[i].user + " - " ;
                messages += ChatClient.formatTime(messageArr[i].date);
                messages += "</span><span class='message'>";
                messages += ": " + messageArr[i].message + "</span><br/>";
            }
        }
        $("#messageLog").append(messages);
        ChatClient.scrollToBottom();
    },

    printUsers: function(userArray) {
        var userCount = userArray.length;
        var userString = "";

    },

    postMessage: function () {

        if(!$.trim($("#userName").val()).length) {
            alert("Please enter a user name to post as.");
            return;
        }

        if(!$.trim($("#message").val()).length) {
            return;
        }

        ChatClient.isPostingMessage = true;

        $.ajax({
            type: "POST",
            url: "chat.py",
            dataType: "json",
            data: { 
                name: $("#userName").val(), 
                message: $("#message").val(),
            },
            success: function(result) {
                if (result.success) {
                    ChatClient.printMessages(result.data);
                    ChatClient.totalMessageCount++;
                }
                $("#message").val("");
            },
            error: function() { 
                alert("failed ajax call."); 
            },
            complete: function() {
                ChatClient.isPostingMessage = false;
            }
        });
    },

    readMessages: function () {
        $.ajax({
            type: "GET",
            url: "chat.py",
            dataType: "json",
            success: function(result) {
                if (result.success && result.data !== undefined && result.data.messages !== undefined) {
                    ChatClient.printMessages(result.data.messages);
                    ChatClient.totalMessageCount = result.data.messages.length;
                }
            },
            error: function() { 
                alert("failed ajax call."); 
            },
            complete: function () {
            }
        });
    },


    toggleTitle: function () {
        var text = document.title;
        if (text == "New Message") { text = "Look Here"; }
        else { text = "New Message" }

        document.title = text;
    },

    poll: function (){
        $.ajax({ 
            url: "chat.py", 
            type: "POST",
            data: {
                poll: true,
                name: $("#userName").val(), 
            },
            success: function(result){
                if (result.success && result.data !== undefined) { 
                    messages = result.data.messages;
                    messageCount = messages.length;
                    users = result.data.users;
                    var shouldToggleTitleBar = messageCount > ChatClient.totalMessageCount &&
                        messages[messageCount - 1].user != $("#userName").val();
                    if (shouldToggleTitleBar) {
                        clearInterval(ChatClient.titleToggleInterval);
                        ChatClient.titleToggleInterval = setInterval(ChatClient.toggleTitle, 1000);
                    }

                    if (messageCount > ChatClient.totalMessageCount) {
                        ChatClient.printMessages(messages); 
                    }
                    ChatClient.totalMessageCount = messageCount;
                }
            }, 
            dataType: "json", 
            //complete: ChatClient.poll, 
            timeout: 60000 
        });
    }
};

$(document).ready(function() {
    $("#newMessage").click(function () {
        if($.trim($("#message").val()).length) {
            ChatClient.postMessage();
        }
    });

    $("#message").keypress(function (e) {
        if (e.keyCode == 13 && !ChatClient.isPostingMessage && $.trim($("#message").val()).length) {
            ChatClient.postMessage();
        }
    });

    $("#message").focus(function() { 
        clearInterval(ChatClient.titleToggleInterval); 
        document.title = "Web Chat";
    } );

    ChatClient.readMessages();
    //ChatClient.poll();
});



