var ws;
function initSocket()
{
    if ("WebSocket" in window)
    {
        console.log("您的浏览器支持 WebSocket!");

        // 打开一个 web socket
        ws = new WebSocket("ws://192.168.1.161:9900");

        ws.onopen = function()
        {
            // Web Socket 已连接上，使用 send() 方法发送数据
            ws.send("发送数据");
            console.log("数据发送中...");
        };

        ws.onmessage = function (evt)
        {
            var received_msg = evt.data;
            console.log("数据已接收...");
        };

        ws.onclose = function()
        {
            // 关闭 websocket
            console.log("连接已关闭...");
        };

    }

    else
    {
        // 浏览器不支持 WebSocket
        console.log("您的浏览器不支持 WebSocket!");
    }
}

function sendmsg(msg) {
    console.log("readyState:"+ws.readyState)
    if(ws.readyState!=1){


    }
    else{
        ws.send(msg);
    }

    //
    
}