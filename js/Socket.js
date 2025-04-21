var websocketHeartbeatJs;


function initSocket(url) {

    try {
        if (websocketHeartbeatJs && websocketHeartbeatJs.ws && websocketHeartbeatJs.ws.readyState == 1) {
            websocketHeartbeatJs.close();
            websocketHeartbeatJs.reconnect();
        }
    } catch (e) {
        console.log(e);
    }


    console.log('new WebsocketHearbeatJs to connect' + url);

    websocketHeartbeatJs = new WebsocketHeartbeatJs({
        url: url,
        pingTimeout: 8000,
        pongTimeout: 8000,
        pingMsg: "HeartBeat"
    });

    console.log('tips: Because use third websocket url, The url may be invalid, in that case submit issue');

    websocketHeartbeatJs.onopen = function () {
        sendHeartCount = 0;
        var msg = "$connect#";
        sendmsg(msg);
        setTimeout(function () {
            layer.msg('wait ' + websocketHeartbeatJs.opts.pingTimeout + ' ms will hava ' + websocketHeartbeatJs.opts.pingMsg);
        }, 1500);

    }


    websocketHeartbeatJs.onmessage = function (e) {
        sendHeartCount = 0;
        layer.msg('onmessage:' + e.data);
        if (e.data == websocketHeartbeatJs.opts.pingMsg && firstHeartbeat) {
            setTimeout(function () {
                layer.msg('`Close your network, wait ' + websocketHeartbeatJs.opts.pingTimeout + websocketHeartbeatJs.opts.pongTimeout + 'ms, websocket will reconnect');
            }, 1500);
            firstHeartbeat = false;
            return false;
        }
        if (e.data == null) {
            return false;
        }

        console.log(e.data);
    }

    websocketHeartbeatJs.onreconnect = function () {
        // layer.msg('reconnecting...');
        // layer.msg('tips: if you network closing, please open network, reconnect will success');
        layer.msg( "你的网络不稳定，正在重连服务器...");
        //语音提示，您已经在线，可以开始抢单了
    }

    websocketHeartbeatJs.onerror = function () {
        console.log('onerror');
    };


}


function sendmsg(pmsg) {
    websocketHeartbeatJs.send(pmsg);
}
