var time = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
    cpu = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    mem = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

var CPU = echarts.init(document.getElementById('CPU'), 'dark');
CPU.setOption({
    title: {text: 'CPU'},
    tooltip: { trigger: 'none' },
    legend: {data: [cpu]},
    calculable: true,
    xAxis: {data: []},
    yAxis: {},
    series: [{name: 'CPU', type: 'line', data: [],}],
    toolbox: {
        show: true,
        feature: {
            magicType: { type: ['line', 'bar'] },
            restore: {},
            saveAsImage: {}
    }}
});

var update_CPU = function (res) {
    CPU.hideLoading();
    cpu.push(parseFloat(res.data[1]));
    if (time.length >= 40) {
        time.shift();
        cpu.shift();
    }
    CPU.setOption({series: [{name: 'CPU', data: cpu}]})
};

var Mem = echarts.init(document.getElementById('Mem'), 'dark');
Mem.setOption({
    title: {text: 'Memory'},
    tooltip: { trigger: 'none' },
    legend: {data: ['mem']},
    calculable: true,
    xAxis: {data: []},
    yAxis: {},
    series: [{name: 'Memory', type: 'line', data: []}],
    toolbox: {
        show: true,
        feature: {
            magicType: { type: ['line', 'bar'] },
            restore: {},
            saveAsImage: {}
    }}
});

var update_Mem = function (res) {
    Mem.hideLoading();
    mem.push(parseFloat(res.data[2]));
    if (time.length >= 40) {
        time.shift();
        mem.shift();
    }
    Mem.setOption({series: [{name: 'Memory', data: mem}]});

};

CPU.showLoading()
Mem.showLoading()
cpu.push(parseFloat(100.0));
mem.push(parseFloat(100.0));
$(document).ready(function () {
    var namespace = '/test';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('server_response', function (res) {
        update_CPU(res);
        update_Mem(res);
    });
});