// 创建场景
const scene = new THREE.Scene();

// 创建相机：透视相机
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 0, 5); // 初始相机位置

// 创建渲染器并设置其大小
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// 创建一个平面几何体和一个基本材质，并将它们组合成一个网格对象
const geometry = new THREE.PlaneBufferGeometry(2, 2);
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
const plane = new THREE.Mesh(geometry, material);
scene.add(plane);


let is_right_down = false;
let is_left_down = false;
let start_mouse = new THREE.Vector2();


function onMouseDown(event) {
    start_mouse.set(
        (event.clientX / window.innerWidth) * 2 - 1,
        -(event.clientY / window.innerHeight) * 2 + 1
    );
    if (event.button === 2) {
        is_right_down = true;
    }else{
        is_left_down = true;
    }
}


function dxy_to_dxyz(y, x, norm_x, norm_y, norm_z){
    y = -y;
    if(norm_x == 0. && norm_z == 0.){
        var x2 = 0.;
        var y2 = 0.;
        var z2 = 1.;
    }else{
        var x2 = 0.;
        var y2 = 1.;
        var z2 = 0.;
    }
    x0 = norm_y * z2 - y2 * norm_z;
    y0 = - norm_x * z2 + norm_z * x2;
    z0 = norm_x * y2 - norm_y * x2;

    x1 = norm_y * z0 - y0 * norm_z;
    y1 = - norm_x * z0 + norm_z * x0;
    z1 = norm_x * y0 - norm_y * x0;

    return [y * x1 - x * x0, y * y1 - x * y0, y * z1 - x * z0];
}


function update_plane(){
    plane.position.x = document.getElementById('x0').value;
    plane.position.y = document.getElementById('y0').value;
    plane.position.z = document.getElementById('z0').value;
    plane.rotation.x = document.getElementById('xn').value;
    plane.rotation.x = document.getElementById('yn').value;
    plane.rotation.x = document.getElementById('zn').value;
}


function update_input(){
    document.getElementById('x0').value = plane.position.x;
    document.getElementById('y0').value = plane.position.y;
    document.getElementById('z0').value = plane.position.z;
    document.getElementById('xn').value = plane.rotation.x;
    document.getElementById('yn').value = plane.rotation.y;
    document.getElementById('zn').value = plane.rotation.z;
}


function onMouseMove(event) {
    const direction = new THREE.Vector3();
    camera.getWorldDirection(direction);
    const mouse = new THREE.Vector2();
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1; 
    dx = mouse.x - start_mouse.x;
    dy = mouse.y - start_mouse.y;
    start_mouse = mouse;
    if(is_right_down){
        const speed = 0.5;
        var rst = dxy_to_dxyz(dx, dy, direction.x, direction.y, direction.z);
        dx = rst[0];
        dy = rst[1];
        dz = rst[2];
        camera.rotation.x += speed * dx;
        camera.rotation.y += speed * dy;
        camera.rotation.z += speed * dz;
    }else if(is_left_down){
        const speed = 0.8;
        var rst = dxy_to_dxyz(dy, -dx, direction.x, direction.y, direction.z);
        dx = rst[0];
        dy = rst[1];
        dz = rst[2];
        plane.position.x += speed * dx;
        plane.position.y += speed * dy;
        plane.position.z += speed * dz;
        update_input();
    }
}

function onMouseUp(event) {
    is_right_down = false;
    is_left_down = false;
}

function onMouseWheel(event) {

    const direction = new THREE.Vector3();
    camera.getWorldDirection(direction);
    
    var x = direction.x;
    var y = direction.y;
    var z = direction.z;

    var speed = 0.5;

    if (event.deltaY > 0) {
        camera.position.x -= speed * x;
        camera.position.y -= speed * y;
        camera.position.z -= speed * z;
    } else {
        camera.position.x += speed * x;
        camera.position.y += speed * y;
        camera.position.z += speed * z;
    }
}



// 处理键盘事件
function onKeyDown(event) {
    const direction = new THREE.Vector3();
    camera.getWorldDirection(direction);
    
    var x = direction.x;
    var y = direction.y;
    var z = direction.z;

    const speed = 1.;

    if(x == 0. && z == 0.){
        var x2 = 0.;
        var y2 = 0.;
        var z2 = 1.;
    }else{
        var x2 = 0.;
        var y2 = 1.;
        var z2 = 0.;
    }

    x0 = y * z2 - y2 * z;
    y0 = - x * z2 + z * x2;
    z0 = x * y2 - y * x2;

    switch (event.key) {
        case 'ArrowUp':
            camera.position.x += speed * x;
            camera.position.y += speed * y;
            camera.position.z += speed * z;
            break;
        case 'ArrowDown':
            camera.position.x -= speed * x;
            camera.position.y -= speed * y;
            camera.position.z -= speed * z;
            break;
        case 'ArrowLeft':
            camera.position.x += speed * x0;
            camera.position.y += speed * y0;
            camera.position.z += speed * z0;
            break;
        case 'ArrowRight':
            camera.position.x -= speed * x0;
            camera.position.y -= speed * y0;
            camera.position.z -= speed * z0;
            break;
    }
}


window.addEventListener('keydown', onKeyDown, false);
window.addEventListener('mousedown', onMouseDown, false);
window.addEventListener('mousemove', onMouseMove, false);
window.addEventListener('mouseup', onMouseUp, false);
window.addEventListener('wheel', onMouseWheel, { passive: false }); 
document.addEventListener('contextmenu', function(event) {
    event.preventDefault();
}, false);


function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();
