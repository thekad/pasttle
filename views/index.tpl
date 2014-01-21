<html>
  <head>
    <title>{{title}} (running pasttle v{{version}})</title>
    <style>
      body {
      font-family: Courier;
      font-size: 12px;
      }

      p {
      margin: 20px;
      }

      a {
      text-decoration: none;
      font-weight: bold;
      }
    </style>
  </head>
  <body>
    <pre>
      pasttle(1)                          PASTTLE                          pasttle(1)

      <strong>NAME</strong>
      pasttle: simple pastebin

      <strong>EXAMPLES</strong>

      To post the output of a given command:

      &lt;command&gt; | curl -F "upload=&lt;-" {{url}}/post && echo

      To post the contents of a file:

      curl -F "upload=&lt;filename.ext" {{url}}/post && echo

      To post the contents of a file and force the syntax to be python:

      curl -F "upload=&lt;filename.ext" -F "syntax=python" \\
      {{url}}/post && echo

      To post the contents of a file and password protect it:

      curl -F "upload=&lt;filename.ext" -F "password=humptydumpty" \\
      {{url}}/post && echo

      You don't like sending plain-text passwords:

      curl -F "upload=&lt;filename.ext" \\
      -F "password=$( echo -n 'bootcat' | sha1sum | cut -c 1-40 )" \\
      -F "is_encrypted=yes" {{url}}/post && echo

      To get the raw contents of a paste (i.e. paste #6):

      curl {{url}}/raw/6

      To get the raw contents of a password-protected paste (i.e. paste #7):

      curl -d "password=foo" {{url}}/raw/7

      Again you don't like sending plain-text passwords:

      curl -d "is_encrypted=yes" \\
      -d "password=$( echo -n 'bootcat' | sha1sum | cut -c 1-40 )" \\
      {{url}}/raw/7

      <strong>HELPERS</strong>

      There are a couple of helper functions in the link below for pasting and
      getting pastes. Import it from your ~/.bash_profile and you should be able
      to use these functions. Creating a ~/.pasttlerc helps you type less too.

      <a href="https://raw.github.com/thekad/pasttle/master/pasttle.bashrc">
        Link
      </a>

      <strong>WEB FORM</strong>

      You can also use this tiny web form to easily upload content.

      <a href="{{url}}/post">
        Link
      </a>
    </pre>
    <p>Copyright &copy; Jorge Gallegos, 2012-2013</p>
    <p>
      <a href="https://github.com/thekad/pasttle">Get the source code</a>
    </p>
  </body>
</html>
