        




// Shortcuts
var map = new AMap.Map('container',{
zoom: 14,
resizeEnable: true,
center: [116.26,40.215]
});
var pots = new Array('昌平首都电影院', '昌平保利影剧院', '昌平大地影院');
var tools = new Array('公交', '步行', '驾车');
var start = "北京化工大学北校区 5号楼";
var current_status = '';
var tmp = '';

//浏览器定位
map.plugin('AMap.Geolocation', function(){
    geolocation = new AMap.Geolocation({
        timeout: 10000,          //超过10秒后停止定位，默认：无穷大
        maximumAge: 0,           //定位结果缓存0毫秒，默认：0
        showButton: true,       
        buttonOffset: new AMap.Pixel(10, 20),//定位按钮与设置的停靠位置的偏移量，默认：Pixel(10, 20)
        zoomToAccuracy:true     
    });
    map.addControl(geolocation);
    AMap.event.addListener(geolocation, 'complete', onComplete);
    AMap.event.addListener(geolocation, 'error', onError);   
});
function onComplete(data) {
    var str=['定位成功'];
    addMarker1(data);
    str.push('经度：' + data.position.getLng());
    str.push('纬度：' + data.position.getLat());
    document.getElementById('tip').innerHTML = str.join('<br>');
}
function onError(data) {
    document.getElementById('tip').innerHTML = '定位失败';
}
//手动定位
// var autoOptions = {
//     input: "tipinput"
// };
// var auto = new AMap.Autocomplete(autoOptions);
// var placeSearch = new AMap.PlaceSearch({
//     map: map
// var placeSearch = new AMap.PlaceSearch({
//     map: map
// });  
// });  
// AMap.event.addListener(auto, "select", select);//注册监听，当选中某条记录时会触发
// function select(e) {
//     placeSearch.setCity(e.poi.adcode);
//     placeSearch.search(e.poi.name);  //关键字查询查询
//  //    marker.on("click", function(e){
//     //  tmp = marker.getPosition();
//     //  LoctoAdress(tmp);
//     // });
// }


//手动定位

// 关键字输入框调用下拉菜单
$('#keyword').focus(function(){
    if ($('#result-box').attr('aria-expanded') == 'false' || $('#result-box').attr('aria-expanded') == undefined)
        $('#result-box').attr('aria-expanded', 'true').addClass('uk-open');
});
$('#keyword').blur(function(){
    if ($('#result-box').attr('aria-expanded') == 'true')
        $('#result-box').attr('aria-expanded', 'false').removeClass('uk-open');
});
// 监听关键字输入框
map.plugin(["AMap.Autocomplete"], function() {  
        //判断是否IE浏览器  
        if (navigator.userAgent.indexOf("MSIE") > 0) {  
            document.getElementById("keyword").onpropertychange = autoSearch;  
        }  
        else {  
            document.getElementById("keyword").oninput = autoSearch;  
        }  
}); 
// 关键字自动检索
function autoSearch() {   
    var keywords = document.getElementById("keyword").value;  
    var auto;    
    var autoOptions = {  
        pageIndex:1,  
        pageSize:10,  
        city: "" //城市，默认全国  
    };  
    autocomplete= new AMap.Autocomplete(autoOptions);
    autocomplete.search(keywords, function(status, result){
        var item = '';
        var items = '';
        if (status == 'complete') {
            for (var i = 0; i < result['count']; i++) {
                item = '<li><a id="' + result['tips'][i]['adcode'] + '" href="#" onMouseDown="select(this)">' + result['tips'][i]['name'] + '</a></li>';
                items += item;
            }
        }
        $('#result').html(items);    // 将检索到的结果覆盖到下拉菜单
    });
}  
// 检索函数
var placeSearch = new AMap.PlaceSearch({
    map: map
});
// 选择下拉菜单的某项后触发检索
function select(e) {
    var adcode = $(e).attr('id');
    var name = $(e).text();
    placeSearch.setCity(adcode);
    placeSearch.search(name);
}



//右键定位
var menu=new ContextMenu(map);
function ContextMenu(map) {
    var me = this;
    this.mouseTool = new AMap.MouseTool(map); 
    this.contextMenuPositon = null;
    var content = '<div class="startpoint"></div>';
    this.contextMenu = new AMap.ContextMenu({isCustom: true, content: content});
    map.on('rightclick', function(e) {
        me.contextMenu.open(map, e.lnglat);
        me.contextMenuPositon = e.lnglat; 
        // alert(me.contextMenuPositon);
        UIkit.notify({
            message: '<i class=\'uk-icon-check\'></i> 坐标：' + me.contextMenuPositon + '',
            status: 'success',
            timeout: 3000,
            pos: 'top-center'
        });
        LoctoAdress(me.contextMenuPositon);
    });
}
ContextMenu.prototype.addMarkerMenu=function () {  
    this.mouseTool.close();
    var marker = new AMap.Marker({
        map: map,
        position: this.contextMenuPositon 
    });
    this.contextMenu.close();
}
//当前位置标记
function addMarker1(d){
    var marker = new AMap.Marker({
        map:map,
        content: '<div class="startpoint"></div>',
        position:[d.position.getLng(), d.position.getLat()]
    });
    marker.on("click", function(e){
        tmp = marker.getPosition();
        LoctoAdress(tmp);
    });
}

//选择影院
function Select_Cinema(i){
    for(var j = 0; j < pots.length; j++)
        if(i == j){
            map.clearMap();
            current_status = pots[i];
            AdresstoLoc(current_status);
        }
}
//电影院标记
function addMarker2(i,d){
    var marker = new AMap.Marker({
        map:map,
        content: '<div class="tag"></div>',
        position:[d.location.getLng(), d.location.getLat()]
    });
    map.plugin('AMap.AdvancedInfoWindow',function(){
        var infoWindow = new AMap.AdvancedInfoWindow({
            content: d.formattedAddress,
            offset: {x:0, y:-30},
            asOrigin: true
        });
        marker.on("click", function(e){
            infoWindow.open(map, marker.getPosition());
        });
    });
}
//周边搜索
function searchNearBy(i,d){
    AMap.plugin('AMap.PlaceSearch', function(){
        var placeSearch = new AMap.PlaceSearch({
            pageSize: 8,
            type: '电影院',
            pageIndex: 1,
            city: "北京", 
            map: map,
            panel: "panel"
        });
        var cpoint = [d.location.getLng(), d.location.getLat()];
        placeSearch.searchNearBy('', cpoint, 5000, function(status, result) {
    });
    });
}
//选择出行方式
function Select_Tool(i){
    map.clearMap( );
    switch(i){
        case 0: 
            //bus
            AMap.plugin('AMap.Transfer', function(){
                var transOptions = new AMap.Transfer({
                    map: map,
                    city: '北京市',
                    panel:'panel',                         
                    policy: AMap.TransferPolicy.LEAST_TIME //乘车策略
                });
                transOptions.search([{keyword: start},{keyword: current_status}], function(status, result){
                });
            });break;
        case 1: 
            //walk
            AMap.plugin('AMap.Walking', function(){
                var walking = new AMap.Walking({
                    map:map,
                    city:'北京',
                    panel: "panel"
                });
                walking.search([{keyword: start},{keyword: current_status}], function(status, result){
                });
            });break;
        case 2: 
            //car
            AMap.plugin('AMap.Driving', function(){
                var driving = new AMap.Driving({
                    map: map,
                    city: '北京',
                    panel: 'panel',
                    policy: AMap.DrivingPolicy.LEAST_DISTANCE
                });
                driving.search([{keyword: start},{keyword: current_status}], function(status, result){
                });
            });break;
        default: break;
    }map.clearMap();
}

//地址-坐标
function AdresstoLoc(data){
    map.plugin('AMap.Geocoder', function(){
        var geocoder = new AMap.Geocoder({
            city: '北京'
        });
        geocoder.getLocation(data, function(status, result) {
            if(status === 'complete' && result.info === 'OK') {
                geocoder_CallBack(result);
            }
            else 
                UIkit.notify({
                    message: status + '',
                    status: 'success',
                    timeout: 3000,
                    pos: 'top-center'
                });
                // kalert(status); 
        }); 
    });
}
function geocoder_CallBack(data){
    var geocode = data.geocodes;
    for(var i = 0; i < geocode.length; i++){
        addMarker2(i, geocode[i]);
        searchNearBy(i, geocode[i]);
    }
    map.setFitView();
}
//坐标-地址
function LoctoAdress(data){
    map.plugin('AMap.Geocoder', function(){
        var geocoder = new AMap.Geocoder({
            radius: 1000,
            extensions: "all"
        });
        geocoder.getAddress(data, function(status, result) {
            if(status === 'complete' && result.info === 'OK') {
                start = result.regeocode.formattedAddress; //返回地址描述
                // alert(start);
                UIkit.notify({
                    message: start + '',
                    status: 'info',
                    timeout: 3000,
                    pos: 'top-center'
                });
            }
            else
                // alert(status); 
                UIkit.notify({
                    message: status + '',
                    status: 'info',
                    timeout: 3000,
                    pos: 'top-center'
                });
        }); 
    });
}
