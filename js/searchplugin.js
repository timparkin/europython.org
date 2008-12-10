function errorMsg(name,ext,cat)
{
  // alert("Netscape 6 or Mozilla is needed to install a sherlock plugin");
  f=document.createElement("form");
  f.setAttribute("name","installform");
  f.setAttribute("method","post");
  f.setAttribute("action","http://mycroft.mozdev.org/error.html");
  fe=document.createElement("input");
  fe.setAttribute("type","hidden");
  fe.setAttribute("name","name");
  fe.setAttribute("value",name);
  f.appendChild(fe);
  fe=document.createElement("input");
  fe.setAttribute("type","hidden");
  fe.setAttribute("name","ext");
  fe.setAttribute("value",ext);
  f.appendChild(fe);
  fe=document.createElement("input");
  fe.setAttribute("type","hidden");
  fe.setAttribute("name","cat");
  fe.setAttribute("value",cat);
  f.appendChild(fe);
  document.getElementsByTagName("body")[0].appendChild(f);
  if (document.installform) { 
    document.installform.submit();
  } else {
    location.href="http://mycroft.mozdev.org/error.html"; //hack for DOM-incompatible browsers
  }
}

function addEngine()
{
 if ((typeof window.sidebar == "object") && (typeof window.sidebar.addSearchEngine == "function")) { 
     window.sidebar.addSearchEngine("http://www.python.org/dev/searchplugin/bugs.src", "http://www.python.org/dev/searchplugin/bugs.png", "bugs", 'General');
     alert("added searchbar");
 } else {
   errorMsg(name,ext,cat);
 } 
}
