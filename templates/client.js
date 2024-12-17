const menus = ['scene', 'match', 'insert', 'path', 'output'];
var uav = {
    dx: 1.5,
}
var xyz0 = {
    xnum: 10,
    ynum: 25,
    dx: 2.,
    xyz0: [0., 0., 0.]
}
var xyze = {
    vec: [0., 1., 0.],
    dx: 2.,
    xyz0: [0., 500., 50.],
    file: null
}

var insert = {
    wh: 300,
    vec: [0., 1., 1.],
    xyz0: [0., 200., 50.],
    seg_idx: 0,
    dis: 3,
    w_max: 10.,
    w_dis: 100.,
    lr: 0.1,
    iter_num: 100,
    mode: "add",
    fea: true
}

var path = {
    seg_idx: -1,
    init_mode: 'rea',
    N: 10,
    dis: 3.,
    seg_dis: 3.,
    cross_dis: 4.,
    cross_seg_dis: 4.,
    w_max: 10.,
    w_dis: 10000.,
    w_seg_dis: 3000.,
    w_cross_dis: 1000.,
    w_cross_seg_dis: 1000.,
    fea: false,
    iter_num: 10,
    lr: 0.1,
    mode: 'div',
    proj_mode: 'clip',
}

var output = {
    nframe: 100,
    mode: 'linear'
}

var default_match_iter_num = 10;
var pid;

var running = false;


function renderMathJax() {
    MathJax.typesetClear();
    MathJax.typesetPromise().then(function () {
      console.log('MathJax has finished re-rendering.');
    }).catch(function (error) {
      console.error('Error during MathJax re-rendering:', error);
    });
}


function print(data){
    const logger = document.getElementById('content');
    logger.innerHTML += "<div class='content-block'>" + data + "<div>";
    logger.scrollTop = logger.scrollHeight;
}


function get(url, data, func){
    var xhr = new XMLHttpRequest();
    var response;
    xhr.open("GET", url, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            response = xhr.responseText;
            func(response);
        }
    };
    xhr.send(null);
}

function post(url, data, func){
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8"); 
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = xhr.responseText;
            func(response);
        }
    };
    xhr.send(data);
}


function stream_post(url, data, func_stream, func_final){
    var xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=utf-8');

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 3) { 
            var response = xhr.responseText;
            var lines = response.split('\n');
            var lastLine = lines[lines.length - 1];
            var epoch = lines.length - 2;
            try {
                func_stream(lastLine, epoch);
            } catch (e) {
            }
        } else if (xhr.readyState === 4) { 
            if(func_final != null){
                var response = xhr.responseText;
                var lines = response.split('\n');
                var lastLine = lines[lines.length - 1];
                func_final(lastLine);
            }
        }
    };

    xhr.send(data);
}


function list_projects(){
    post(
        "./list_projects", null, function(resp){
            var resp = JSON.parse(resp);
            var data = "<table><tr>";
            var h = true;
            for (const pid in resp){
                if(h){
                    data += `<th>pid</th>`;
                    for(var key in resp[pid]){
                        if(key == "seg_num"){
                            key = "段数";
                        }else if(key == "N"){
                            key = "点数";
                        }else if(key == "n"){
                            key = "UAV数";
                        }else if(key == "running"){
                            key = "是否运行";
                        }else if(key == "time"){
                            key = "创建时间";
                        }
                        data += `<th>${key}</th>`;
                    }
                    data += '</tr>';
                    h = false;
                }
                data += `<tr><td>${pid}</td>`;
                for(const key in resp[pid]){
                    data += `<td>${resp[pid][key]}</td>`;
                }
                data += '</tr>';
            }
            data += "</table>";
            print(data);
        }
    )
}

function change_menu(cur){
    for(var i=0; i<menus.length; i++){
        var menu = menus[i];
        if(menu == cur){
            document.getElementById(menu).style.display = '';
            document.getElementById(menu + "_menu").style.backgroundColor = '#46484a';
        }else{
            document.getElementById(menu).style.display = 'none'
            document.getElementById(menu + "_menu").style.backgroundColor = '';
        }
    }
}

function clear_log(){
    document.getElementById('content').innerHTML = "";
}

function create_project(){
    uav.dx = document.getElementById('uav_dx').value;
    xyz0.xnum = document.getElementById('xyz0_xnum').value;
    xyz0.ynum = document.getElementById('xyz0_ynum').value;
    xyz0.dx = document.getElementById('xyz0_dx').value;
    xyz0.xyz0[0] = document.getElementById('xyz0_x').value;
    xyz0.xyz0[1] = document.getElementById('xyz0_y').value;
    xyz0.xyz0[2] = document.getElementById('xyz0_z').value;
    xyze.vec[0] = document.getElementById('xyze_vec_x').value;
    xyze.vec[1] = document.getElementById('xyze_vec_y').value;
    xyze.vec[2] = document.getElementById('xyze_vec_z').value;
    xyze.dx = document.getElementById('xyze_dx').value;
    xyze.xyz0[0] = document.getElementById('xyze_x').value;
    xyze.xyz0[1] = document.getElementById('xyze_y').value;
    xyze.xyz0[2] = document.getElementById('xyze_z').value;
    xyze.file = document.getElementById('xyze_file').value;      

    var image = document.getElementById('xyze_file').files[0];
    if (!image) {
        window.alert('未识别到图片，默认终点为”国“字');
        post("./create_project", JSON.stringify({
            uav: uav,
            xyz0: xyz0,
            xyze: xyze,
            image: null
        }), function(resp){
            try{
                resp = JSON.parse(resp);
                if(resp['status'] == 'succeed'){
                    pid = resp['pid'];
                    document.getElementById('pid').value = pid;
                    print(`成功创建: ${pid}`);
                }else{
                    print(resp['status']);
                }
            }catch{
                print(resp);
            }
            running = false;
        })
    }else{
        const reader = new FileReader();
        reader.onload = function(event) {
            const base64String = event.target.result;
            var image_base64 = base64String.split(',')[1];
            post("./create_project", JSON.stringify({
                uav: uav,
                xyz0: xyz0,
                xyze: xyze,
                image: image_base64
            }), function(resp){
                try{
                    resp = JSON.parse(resp);
                    if(resp['status'] == 'succeed'){
                        pid = resp['pid'];
                        document.getElementById('pid').value = pid;
                        print(`成功创建: ${pid}`);
                    }else{
                        print(resp['status']);
                    }
                }catch{
                    print(resp);
                }
                running = false;
            })
        };
        reader.readAsDataURL(image);
    }

}


function reset_uav(){
    document.getElementById('uav_dx').value = uav.dx;
    document.getElementById('xyz0_xnum').value = xyz0.xnum;
    document.getElementById('xyz0_ynum').value = xyz0.ynum;
    document.getElementById('xyz0_dx').value = xyz0.dx;
    document.getElementById('xyz0_x').value = xyz0.xyz0[0];
    document.getElementById('xyz0_y').value = xyz0.xyz0[1];
    document.getElementById('xyz0_z').value = xyz0.xyz0[2];
    document.getElementById('xyze_vec_x').value = xyze.vec[0];
    document.getElementById('xyze_vec_y').value = xyze.vec[1];
    document.getElementById('xyze_vec_z').value = xyze.vec[2];
    document.getElementById('xyze_dx').value = xyze.dx;
    document.getElementById('xyze_x').value = xyze.xyz0[0];
    document.getElementById('xyze_y').value = xyze.xyz0[1];
    document.getElementById('xyze_z').value = xyze.xyz0[2];
    document.getElementById('xyze_file').files[0] = xyze.file;
}

function reset_match(){
    document.getElementById('match_iter_num').value = default_match_iter_num;
}

function load_project(){
    var p = document.getElementById('pid').value;
    if(p == null || p.length == 0){
        print('Empty pid');
        return false;
    }
    post("./load_project", p, function(resp){
        resp = JSON.parse(resp);
        if(resp['status'] != 'succeed'){
            print(resp['status']);
        }else{
            pid = resp['pid'];
            uav = resp['setting']['uav'];
            xyz0 = resp['setting']['xyz0'];
            xyze = resp['setting']['xyze'];
            reset_uav();
            print(`成功加载: ${pid}`);
        }
    })
}

function delete_project(){
    var p = document.getElementById('pid').value;
    if(p == null || p.length == 0){
        print('Empty pid');
        return false;
    }
    post("./delete_project", p, function(resp){
        resp = JSON.parse(resp);
        if(resp['status'] != 'succeed'){
            print(resp['status']);
        }else{
            print(`成功删除 ${resp['pid']}.`);
            if(pid == p){
                pid = null;
                print(`当前pid ${p}已无效`);
                document.getElementById('pid').value = '';
            }
        }
    })
}

function set_match(){
    match_iter_num = Number(document.getElementById('match_iter_num').value);
}

function start_match(){
    if(pid == null || pid.length == 0){
        print('Empty pid');
        return false;
    }
    print("开始匹配，耐心等待");
    stream_post("./start_match", JSON.stringify({
        pid: pid,
        iter_num: document.getElementById('match_iter_num').value
    }), async function(resp, epoch){
        var resp = JSON.parse(resp)
        print(`迭代第 (${epoch} / ${document.getElementById('match_iter_num').value}) 次`);
    }, function(resp){
        var resp = JSON.parse(resp);
        try{
            if(resp['status']){
                print(resp['status']);
            }
        }catch{

        }
        // print(resp);
        resp = resp['upper'];
        print(`迭代完成, 当前最大位移为${resp[0]}, 平均位移为${resp[1]}.`);
    })
}


function stop_running(){
    if(pid == null || pid.length == 0){
        print('Empty pid');
        return false;
    }
    post("./stop_running", pid, function(resp){
        var resp = JSON.parse(resp);
        if(resp['status'] != 'succeed'){
            print(resp['status']);
        }else{
            print(`停止运行 ${resp['pid']}`);
        }
    })
}


function initial_body(){
    reset_uav();
    reset_match();
    reset_insert();
    reset_path();
    reset_output();
}


function reset_insert(){
    document.getElementById('insert_wh').value = insert.wh;
    document.getElementById('insert_vec_x').value = insert.vec[0];
    document.getElementById('insert_vec_y').value = insert.vec[1];
    document.getElementById('insert_vec_z').value = insert.vec[2];
    document.getElementById('insert_x').value = insert.xyz0[0];
    document.getElementById('insert_y').value = insert.xyz0[1];
    document.getElementById('insert_z').value = insert.xyz0[2];
    document.getElementById('insert_seg_idx').value = insert.seg_idx;
    document.getElementById('insert_dis').value = insert.dis;
    document.getElementById('insert_w_max').value = insert.w_max;
    document.getElementById('insert_w_dis').value = insert.w_dis;
    document.getElementById('insert_lr').value = insert.lr;
    document.getElementById('insert_iter_num').value = insert.iter_num;
    document.getElementById('insert_mode').value = insert.mode;
    document.getElementById('insert_fea').checked = insert.fea;
    draw_eq_insert();
}


function save_insert(){
    insert.wh = Number(document.getElementById('insert_wh').value);
    insert.vec[0] = Number(document.getElementById('insert_vec_x').value);
    insert.vec[1] = Number(document.getElementById('insert_vec_y').value);
    insert.vec[2] = Number(document.getElementById('insert_vec_z').value);
    insert.xyz0[0] = Number(document.getElementById('insert_x').value);
    insert.xyz0[1] = Number(document.getElementById('insert_y').value);
    insert.xyz0[2] = Number(document.getElementById('insert_z').value);
    insert.seg_idx = Number(document.getElementById('insert_seg_idx').value);
    insert.dis = Number(document.getElementById('insert_dis').value);
    insert.w_max = Number(document.getElementById('insert_w_max').value);
    insert.w_dis = Number(document.getElementById('insert_w_dis').value);
    insert.lr = Number(document.getElementById('insert_lr').value);
    insert.iter_num = Number(document.getElementById('insert_iter_num').value);
    insert.mode = document.getElementById('insert_mode').value;
    insert.fea = document.getElementById('insert_fea').checked;
}


function start_insert(){
    if(pid == null){
        window.alert("Empty pid");
        return false;
    }
    var insert = {
        wh: Number(document.getElementById('insert_wh').value),
        vec: [
            Number(document.getElementById('insert_vec_x').value),
            Number(document.getElementById('insert_vec_y').value),
            Number(document.getElementById('insert_vec_z').value)
        ],
        xyz0: [
            Number(document.getElementById('insert_x').value),
            Number(document.getElementById('insert_y').value),
            Number(document.getElementById('insert_z').value)
        ],
        seg_idx: Number(document.getElementById('insert_seg_idx').value),
        dis: Number(document.getElementById('insert_dis').value),
        w_max: Number(document.getElementById('insert_w_max').value),
        w_dis: Number(document.getElementById('insert_w_dis').value),
        lr: Number(document.getElementById('insert_lr').value),
        iter_num: Number(document.getElementById('insert_iter_num').value),
        mode: document.getElementById('insert_mode').value,
        fea: Boolean(document.getElementById('insert_fea').checked),
        pid: pid
    }
    stream_post("./start_insert", JSON.stringify(insert), async function(resp, epoch){
        var resp = JSON.parse(resp);
        if(resp['status'] != 'succeed'){
            print(resp['status']);
        }else{
            print(`迭代第(${resp['epoch']}/${insert.iter_num})次, 损失值${resp['loss'].toFixed(2)}, 小距离对数${resp['danger_num']}`);
        }
    }, function(resp){
        var resp = JSON.parse(resp);
        print(`迭代完成, 损失值${resp['loss']}, 小距离对数${resp['danger_num']}, 平均距离${resp['avg_seg']}, 最大距离${resp['max_seg']}`);
    })
}


function cancel_insert(){
    var seg_idx = document.getElementById('insert_cancel_seg_idx').value;
    if(pid == null){
        window.alert("Empty pid");
        return false;
    }
    if(seg_idx == null || seg_idx.length == 0){
        window.alert("Empty sid");
        return false;
    }
    post("./cancel_insert", JSON.stringify({
        pid: pid,
        seg_idx: seg_idx
    }), function(resp){
        var resp = JSON.parse(resp);
        if(resp['status'] != 'succeed'){
            print(resp['status']);
        }else{
            print(`成功合并 ${resp['pid']} 的 ${resp['seg_idx']}`);
        }
    })
}


function reset_path(){
    document.getElementById('path_seg_idx').value = path.seg_idx;
    document.getElementById('path_init_mode').value = path.init_mode;
    document.getElementById('path_N').value = path.N;
    document.getElementById('path_dis').value = path.dis;
    document.getElementById('path_seg_dis').value = path.seg_dis;
    document.getElementById('path_cross_dis').value = path.cross_dis;
    document.getElementById('path_cross_seg_dis').value = path.cross_seg_dis;
    document.getElementById('path_w_max').value = path.w_max;
    document.getElementById('path_w_dis').value = path.w_dis;
    document.getElementById('path_w_seg_dis').value = path.w_seg_dis;
    document.getElementById('path_w_cross_dis').value = path.w_cross_dis;
    document.getElementById('path_w_cross_seg_dis').value = path.w_cross_seg_dis;
    document.getElementById('path_fea').checked = path.fea;
    document.getElementById('path_iter_num').value = path.iter_num;
    document.getElementById('path_lr').value = path.lr;
    document.getElementById('path_mode').value = path.mode;
    document.getElementById('path_proj_mode').value = path.proj_mode;
    draw_eq_path();
}


function save_path(){
    path.seg_idx = document.getElementById('path_seg_idx').value;
    path.init_mode = document.getElementById('path_init_mode').value;
    path.N = document.getElementById('path_N').value;
    path.dis = document.getElementById('path_dis').value;
    path.seg_dis = document.getElementById('path_seg_dis').value;
    path.cross_dis = document.getElementById('path_cross_dis').value;
    path.cross_seg_dis = document.getElementById('path_cross_seg_dis').value;
    path.w_max = document.getElementById('path_w_max').value;
    path.w_dis = document.getElementById('path_w_dis').value;
    path.w_seg_dis = document.getElementById('path_w_seg_dis').value;
    path.w_cross_dis = document.getElementById('path_w_cross_dis').value;
    path.w_cross_seg_dis = document.getElementById('path_w_cross_seg_dis').value;
    path.fea = document.getElementById('path_fea').checked;
    path.iter_num = document.getElementById('path_iter_num').value;
    path.lr = document.getElementById('path_lr').value;
    path.mode = document.getElementById('path_mode').value;
    path.proj_mode = document.getElementById('path_proj_mode').value;
}


function start_path(){
    if(pid == null){
        window.alert("Empty pid");
        return false;
    }
    var path = {
        seg_idx: Number(document.getElementById('path_seg_idx').value),
        init_mode: document.getElementById('path_init_mode').value,
        N: Number(document.getElementById('path_N').value),
        dis: Number(document.getElementById('path_dis').value),
        seg_dis: Number(document.getElementById('path_seg_dis').value),
        cross_dis: Number(document.getElementById('path_cross_dis').value),
        cross_seg_dis: Number(document.getElementById('path_cross_seg_dis').value),
        w_max: Number(document.getElementById('path_w_max').value),
        w_dis: Number(document.getElementById('path_w_dis').value),
        w_seg_dis: Number(document.getElementById('path_w_seg_dis').value),
        w_cross_dis: Number(document.getElementById('path_w_cross_dis').value),
        w_cross_seg_dis: Number(document.getElementById('path_w_cross_seg_dis').value),
        fea: Boolean(document.getElementById('path_fea').checked),
        iter_num: Number(document.getElementById('path_iter_num').value),
        lr: Number(document.getElementById('path_lr').value),
        mode: document.getElementById('path_mode').value,
        proj_mode: document.getElementById('path_proj_mode').value,
        pid: pid
    }
    stream_post("./start_path", JSON.stringify(path), async function(resp, epoch){
        var resp = JSON.parse(resp);
        if(resp['status'] != 'succeed'){
            print(resp['status']);
        }else{
            if(resp['stage'] != 'solve'){
                print(resp['stage']);
            }else{
                print(`迭代第(${resp['epoch']}/${path.iter_num})次, 损失值${resp['loss']}`);
            }
        }
    }, function(resp){
        var resp = JSON.parse(resp);
        print(`迭代第(${resp['epoch']}/${path.iter_num})次, 损失值${resp['loss']}, 平均长度${resp['avg_len']},
             最大长度${resp['max_len']}, 小距离UAV对数${resp['dis_num']}, 小距离线对数${resp['seg_num']},
              小距离点线对数${resp['cross_num']}, 小距离线线对数${resp['cross_seg_num']}`);
    })
}


function reset_output(){
    document.getElementById('output_nframe').value = output.nframe;
    document.getElementById('output_mode').value = output.mode;
}


function save_output(){
    output.nframe = Number(document.getElementById('output_nframe').value);
    output.mode = document.getElementById('output_mode').value;
}


function download_json(jsonData, name){
    const jsonString = JSON.stringify(jsonData, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
    document.body.removeChild(a);
}


function start_output(){
    if(pid == null){
        window.alert("Empty pid");
        return false;
    }
    var dis = uav.dx;
    print('开始输出，耐心等待');
    post("./start_output", JSON.stringify({
        pid: pid,
        dis: dis,
        mode: document.getElementById('output_mode').value,
        nframe: Number(document.getElementById('output_nframe').value)
    }), function(resp){
        var resp = JSON.parse(resp);
        if(resp['status'] != 'succeed'){
            print(resp['status']);
        }else{
            print(`碰撞次数: ${resp['col_num']}, 碰撞占比: ${resp['col_rate']}, 算法状态: ${resp['rst']}`);
            var jsonData = resp['result'];
            download_json(jsonData, `${pid}.json`);
        }
    })
}


function view_projects(){
    
    var p = document.getElementById('pid').value;
    if(p == null || p.length == 0){
        print('Empty pid');
        return false;
    }
    post("./view_projects", p, function(resp){
        resp = JSON.parse(resp);
        if(resp['status'] != 'succeed'){
            print(resp['status']);
        }else{
            print(`<img src="${resp['image']}" alt="">`);
        }
    })
}


function draw_eq_insert(){
    var ist = {
        wh: Number(document.getElementById('insert_wh').value),
        vec: [
            Number(document.getElementById('insert_vec_x').value),
            Number(document.getElementById('insert_vec_y').value),
            Number(document.getElementById('insert_vec_z').value)
        ],
        xyz0: [
            Number(document.getElementById('insert_x').value),
            Number(document.getElementById('insert_y').value),
            Number(document.getElementById('insert_z').value)
        ],
        seg_idx: Number(document.getElementById('insert_seg_idx').value),
        dis: Number(document.getElementById('insert_dis').value),
        w_max: Number(document.getElementById('insert_w_max').value),
        w_dis: Number(document.getElementById('insert_w_dis').value),
        lr: Number(document.getElementById('insert_lr').value),
        iter_num: Number(document.getElementById('insert_iter_num').value),
        mode: document.getElementById('insert_mode').value,
        fea: Boolean(document.getElementById('insert_fea').checked),
        pid: pid
    }

    if(ist.mode == 'add'){
        var text = `$\\frac{1}{n} \\sum_{k} l_k + ${ist.w_max} \\max_{k} l_k - \\frac{${ist.w_dis}}{n} \\sum_{d_{mn}<${ist.dis}} d_{mn} $ `;
    }else{
        var text = `$\\frac{1}{n} \\sum_{k} l_k + ${ist.w_max} \\max_{k} l_k + \\frac{${ist.w_dis}}{n} \\sum_{d_{mn}<${ist.dis}} \\frac{${ist.dis}}{d_{mn}} $`;
    }

    document.getElementById('eq_insert').innerHTML = text;
    renderMathJax();
}

function draw_eq_path(){
    var pth = {
        seg_idx: Number(document.getElementById('path_seg_idx').value),
        init_mode: document.getElementById('path_init_mode').value,
        N: Number(document.getElementById('path_N').value),
        dis: Number(document.getElementById('path_dis').value),
        seg_dis: Number(document.getElementById('path_seg_dis').value),
        cross_dis: Number(document.getElementById('path_cross_dis').value),
        cross_seg_dis: Number(document.getElementById('path_cross_seg_dis').value),
        w_max: Number(document.getElementById('path_w_max').value),
        w_dis: Number(document.getElementById('path_w_dis').value),
        w_seg_dis: Number(document.getElementById('path_w_seg_dis').value),
        w_cross_dis: Number(document.getElementById('path_w_cross_dis').value),
        w_cross_seg_dis: Number(document.getElementById('path_w_cross_seg_dis').value),
        fea: Boolean(document.getElementById('path_fea').checked),
        iter_num: Number(document.getElementById('path_iter_num').value),
        lr: Number(document.getElementById('path_lr').value),
        mode: document.getElementById('path_mode').value,
        proj_mode: document.getElementById('path_proj_mode').value,
        pid: pid
    }

    if(pth.mode == 'add'){
        var text = `$\\frac{1}{n} \\sum_{k} l_k + ${pth.w_max} \\max_{k} l_k $<br>
        $- \\frac{${pth.w_dis}}{n} \\sum_{d_{UAV}(x_m^i, x_n^i)<${pth.dis}} d_{UAV}(x_m^i, d_n^i) $ <br>
        $- \\frac{${pth.w_seg_dis}}{n} \\sum_{d_{平行}(s_m^i, s_n^i)<${pth.seg_dis}} d_{平行}(s_m^i, s_n^i)$<br>
        $- \\frac{${pth.w_cross_dis}}{n} \\sum_{d_{点线}(x_m^i, s_n^i)<${pth.cross_dis}}d_{点线}(x_m^i, s_n^i)$<br>
        $- \\frac{${pth.w_cross_seg_dis}}{n} \\sum_{d_{交叉}(s_m^i, s_n^i)<${pth.cross_seg_dis}}d_{交叉}(s_m^i, s_n^i) $`;
    }else{
        var text = `$\\frac{1}{n} \\sum_{k} l_k + ${pth.w_max} \\max_{k} l_k $<br>
        $+ \\frac{${pth.w_dis}}{n} \\sum_{d_{UAV}(x_m^i, x_n^i)<${pth.dis}} \\frac{${pth.dis}}{d_{UAV}(x_m^i, d_n^i)} $ <br>
        $+ \\frac{${pth.w_seg_dis}}{n} \\sum_{d_{平行}(s_m^i, s_n^i)<${pth.seg_dis}} \\frac{${pth.seg_dis}}{d_{平行}(s_m^i, s_n^i)}$<br>
        $+ \\frac{${pth.w_cross_dis}}{n} \\sum_{d_{点线}(x_m^i, s_n^i)<${pth.cross_dis}}\\frac{${pth.cross_dis}}{d_{点线}(x_m^i, s_n^i)}$<br>
        $+ \\frac{${pth.w_cross_seg_dis}}{n} \\sum_{d_{交叉}(s_m^i, s_n^i)<${pth.cross_seg_dis}}\\frac{${pth.cross_seg_dis}}{d_{交叉}(s_m^i, s_n^i)} $`;
    }

    document.getElementById('eq_path').innerHTML = text;
    renderMathJax();
}


function about(){
    if(document.getElementById('iframe').style.display != 'none'){
        document.getElementById('iframe').style.display = 'none';
        document.getElementById('about').style.display = 'block';
        document.getElementById('about_btn').innerHTML = '模拟';
    }else{
        document.getElementById('about').style.display = 'none';
        document.getElementById('iframe').style.display = 'block';
        document.getElementById('about_btn').innerHTML = '文档';
    }
}


function split_all(){
    if(pid == null){
        window.alert("Empty pid");
        return false;
    }
    nframe = Number(document.getElementById('output_nframe').value);
    post('./split_all', JSON.stringify({
        pid: pid,
        nframe: nframe
    }), function(resp){
        var resp = JSON.parse(resp);
        if(resp['status'] == 'succeed'){
            print("划分完毕");
        }else{
            print(resp['status']);
        }
    })
}


function output_config(){
    save_insert();
    save_output();
    save_path();
    var json_data = {
        uav: uav,
        xyz0: xyz0,
        xyze: xyze,
        match: document.getElementById('match_iter_num').value,
        insert: insert,
        path: path,
        output: output
    }
    download_json(json_data, 'config.json');
}


function input_config(){
    document.getElementById('input_config').click();
}


function read_config(){
    const file = document.getElementById('input_config').files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        try {
            var jsonData = JSON.parse(e.target.result);
            uav = jsonData.uav;
            xyz0 = jsonData.xyz0;
            xyze = jsonData.xyze;
            document.getElementById('match_iter_num').value = jsonData.match;
            insert = jsonData.insert;
            path = jsonData.path;
            output = jsonData.output;
            initial_body();
            print('成功导入');
        } catch (error) {
            window.alert(error.message);
        }
    };

    reader.readAsText(file);
}