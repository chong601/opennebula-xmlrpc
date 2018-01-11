function startVMXHR()
{
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange=function(){
        if(this.readyState==4 && this.status==200)
        {
            document.getElementById("start-result").innerHTML=this.responseText
        }
    }
    xhr.open("POST","/start",true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("objectid="+document.getElementById("start-objectid").value)
}

function stopVMXHR()
{
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange=function(){
        if(this.readyState==4 && this.status==200)
        {
            document.getElementById("stop-result").innerHTML=this.responseText
        }
    }
    xhr.open("POST","/stop",true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("objectid="+document.getElementById("stop-objectid").value)
}

function statusVMXHR()
{
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange=function(){
        if(this.readyState==4 && this.status==200)
        {
            document.getElementById("status-result").innerHTML=this.responseText
        }
    }
    xhr.open("POST","/status",true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("objectid="+document.getElementById("status-objectid").value)
}

function statusallVMXHR()
{
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange=function(){
        if(this.readyState==4 && this.status==200)
        {
            document.getElementById("statusall-result").innerHTML=this.responseText
        }
    }
    xhr.open("POST","/statusall",true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send()
}

function createVMXHR()
{
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange=function(){
        if(this.readyState==4 && this.status==200)
        {
            document.getElementById("create-result").innerHTML=this.responseText
        }
    }
    xhr.open("POST","/create",true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("objectid="+document.getElementById("create-objectid").value)
}