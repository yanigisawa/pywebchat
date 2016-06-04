<html>
<head>
<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<title>Web Chat</title>
    <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.0.3/css/bootstrap.min.css">
    <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.0.3/css/bootstrap-theme.min.css">
    <link rel="stylesheet" href="/static/main.css">
</head>
<body>
<meta name="viewport" content="width=device-width, initial-scale=1"> 

<div class="usersContainer">
    <h3>Users</h3>
    <div id="users"></div>
</div>

<div id="messageLog"></div>

<div class="input"> 
	<input type="text" id="userName" value="" placeholder="Name" class="inputs mousetrap"></input>
	<input type="text" id="message" value="" placeholder="Message" class="inputs mousetrap"/>
	<input type="button" id="newMessage" name="newMessage" value="Post" class="css_button" />
    <input type="button" id="refresh" name="refresh" value="Refresh" class="css_button" />
</div>

<div id="console"></div>

{% raw %}
<script id="message-template" type="text/x-handlebars-template">
  {{#each messages}}
    <span class='{{ cssClass }}'>
    <span class='metaData'>{{ user }} {{ date }}:</span>
    <span class='message'>{{{ message  }}}</span></span>
  {{/each}}
</script>
{% endraw %}


{% raw %}
<script id="user-template" type="text/x-handlebars-template">
  {{#each users}}
    <img src="/static/img/{{ image }}.png" height="16px" width="16px" />
    <span class='user'> {{ name }}</span></br>
  {{/each}}
</script>
{% endraw %}

<script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.1/jquery.min.js"></script>
<script src="/static/js/handlebars-v2.0.0.js"></script>
<script src="/static/js/jquery.hotkeys.js"></script>
<script src="/static/js/mousetrap.min.js"></script>
<script>
  var config = { room : "{{ room }}" };
</script>
<script src="/static/js/chatClient.js"></script>
</body>
</html>
