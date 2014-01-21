<html>
  <head>
    <title>Pasttle</title>
  </head>
  <body>
    <ul>
      % for paste in pastes:
      <li><a href="{{paste.id}}">Paste #{{paste.id}}, {{paste.filename or u''}} ({{paste.mimetype}}) {{paste.created}}</a></li>
      % end
    </ul>
  </body>
</html>
