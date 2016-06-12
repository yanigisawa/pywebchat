
var HistoryClient = function(messageLog) { 
  var _messageLog = messageLog;
  var source = $("#message-template").html();
  var messageTemplate = Handlebars.compile(source);

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

  this.printMessages = function(messageArr, key) {
    var messages = [];
    var messageCount = messageArr.length;
    var room = "";
    var cssClass = "generalUserStyle";
    var alternate = false;
    for(var i = 0; i < messageCount; i++) {
      if (room == "") { room = messageArr[i].room;}

      if (room != messageArr[i].room) {
        room = messageArr[i].room;
        cssClass = "generalUserstyle " + (alternate ? " alternateRoom" : "");
        alternate = !alternate;
      }

      messageArr[i].cssClass = cssClass; 
      messageArr[i].date = formatTime(messageArr[i].date);
    }

    var html = messageTemplate({ messages: messageArr});
    $("#messages_" + key).html(html);
  };

  this.click = function(key) {
    var that = this;
    $("#spinner_" + key).toggle();
    $.ajax({
      type: "GET",
      url: "history/" + key,
      dataType: "json",
      success: function (result) {
        that.printMessages(result, key);
      },
      error: function() { 
        $("#messageLog").append("### - Failed to read messages from server - ###</br>"); 
      },
      complete: function () {
        $("#spinner_" + key).toggle();
      }
    });
  }
};


$(document).ready(function() {
  $(".historyLink").click(function () {
    var historyClient = new HistoryClient($("#messageLog"));
    historyClient.click(this.id);
    return false;
  });
});

