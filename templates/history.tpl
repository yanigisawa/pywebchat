<html>
<head>
<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<title>Web Chat History</title>
    <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.0.3/css/bootstrap.min.css">
    <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.0.3/css/bootstrap-theme.min.css">
    <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.css">
    <link rel="stylesheet" href="/static/history.css">
    <script src="https://use.fontawesome.com/66e05d1866.js"></script>
</head>
<body>
<meta name="viewport" content="width=device-width, initial-scale=1"> 

{% for key in keyList %}

  <a href="" class="historyLink" id="{{ key }}">{{ key }}</a>
  <i class="fa fa-spinner fa-spin" style="display: none;" id="spinner_{{ key }}"></i>
  <div id="messages_{{ key }}" class="historyMessages"></div>

{% endfor %}

{% raw %}
<script id="message-template" type="text/x-handlebars-template">
  {{#each messages}}
    <span class="{{ cssClass }}">
    <span class='metaData'>{{ room }} - {{ user }} {{ date }}:</span>
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
<script src="/static/js/historyClient.js"></script>
</body>
</html>
