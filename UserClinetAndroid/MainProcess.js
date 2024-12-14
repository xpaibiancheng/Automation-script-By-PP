"ui";

Announcements();

let HostAddress = ""


//悬浮窗打开的一个标志 
var floatWindowFlag = false;
/**
 * 功能: 获取并显示用户公告内容，并提供复制到剪切板的功能。
 * 
 * 该函数通过发送 HTTP GET 请求从指定 URL 获取公告内容，若请求成功，解析并展示公告的标题和内容。
 * 用户可以选择点击“确定”按钮来将公告内容复制到剪切板。
 * 
 * 参数: 无
 * 
 * 返回值: 无
 * 
 * 异常处理: 如果请求失败或返回状态码不是 200，会在 UI 上显示错误提示。
 */
function Announcements() {
    threads.start(() => {
        // 发送请求验证密钥
        let url = HostAddress + "";
        try{
            // 使用 http.postJson 发送请求，并在回调中处理响应
            var  response = http.get(url)
            console.log("后端的回复:", response);
            if(response.statusCode == 200){
                let info = response.body.json(); // 解析为 JSON 对象
                console.log(info);
                var confirmInfo = confirm(info.announcement.title,info.announcement.content+"\n点击确定复制")
                if(confirmInfo){
                    setClip(info.announcement.content);
                    alert("已复制到剪切板");
                    
                }
            }else{
                console.log(e);
                ui.run(() => {
                    toast("公告获取错误: " + e.message);
                });
            }
        }catch (e) {
            // 请求出错
            console.log(e);
            ui.run(() => {
                toast("请求失败: " + e.message);
            });
        }
        
    });

}   
// 创建简单的界面
ui.layout(
    <vertical id="containerAll" padding="16">
        <img w="80" h="80" circle="true" marginLeft="120" marginTop="30" marginBottom="20" src=""/>

        <text textSize="25sp" gravity="center" textColor="black" id="myText" line="2"/>
        
        <input id="name" hint="请输入正确卡密" />

        <button id="ok" text="确定"/>

        <text textSize="20sp" gravity="left" textColor="#2be22c" id="UserTextInfo" line="1.75"></text>
        
        <text textSize="15sp" gravity="left" textColor="#808080" id="TextTips" line="2"/>

    </vertical>
);

// 通过\n换行
ui.myText.setText("皮皮答题辅助脚本工具\nversion 1.0.0\n");

ui.UserTextInfo.setText("");

ui.TextTips.setText("1. 请输入正确卡密，保证卡密次数、时长、状态等信息有效。\n2. 答题脚本在自动答题的时候请勿进入其他界面，否则会导致答题失败。\n3. 脚本运行过程中请不要手动关闭脚本，否则会导致答题失败。\n4.请勿乱点击脚本的开始工作按钮，否则会扣有效次数。\n5.答题结束后悬浮窗口会自动关闭，对于准确率不达标的答题会返回答题次数，无特殊情况请勿点击关闭按钮")

/**
 * 功能: 处理用户输入的密钥，验证密钥的有效性，并展示相关信息。
 * 
 * 该函数监听 UI 上的“确定”按钮点击事件，获取用户输入的密钥并验证其有效性。如果密钥有效，
 * 则返回相关信息（如次数、时长、开通日期等），并更新 UI 显示密钥信息及一个“开始工作”按钮。
 * 如果密钥为空，则会弹出提示信息。
 * 
 * 参数: 无
 * 
 * 返回值: 无
 * 
 * 异常处理: 如果请求失败或响应不符合预期，会通过 `toast` 提示用户错误信息。
 */
ui.ok.setOnClickListener(() => {
    let key = ui.name.text(); // 获取输入的密钥
    if (key.length == 0) {
        ui.run(() => {
            toast("不能为空");
        });
        return;
    }
    console.log("密钥信息", key);
    
    // 启动后台线程进行网络请求
    threads.start(() => {
        // 发送请求验证密钥
        let url =  HostAddress + "";
        try {
            // 使用 http.postJson 发送请求，并在回调中处理响应
            var response = http.postJson(url, { keySecret: key });

            let info = response.body.json(); // 解析为 JSON 对象

            console.log("解码后的后端响应:", info);

            // 判断后端是否返回成功
            if (info.success) {

                let displayMessage = `\n次数: ${info.data.count} 次\n时长: ${info.data.duration} 天\n开通日期: ${info.data.generate_date}\n已使用次数: ${info.data.use_count}\n状态: ${info.message}\n`;

                // UI更新：隐藏“确定按钮”，禁用输入框，显示密钥信息，并添加“开始工作”按钮
                ui.run(() => {

                    // 隐藏“确定”按钮
                    ui.ok.visibility = 8;

                    // 禁用输入框
                    ui.name.setEnabled(false);

                    // 显示密钥信息
                    ui.UserTextInfo.setText(displayMessage);

                    // 添加“开始工作”按钮
                    // 动态更新布局，添加“开始工作”按钮
                    // 动态添加“开始工作”按钮
                    let startButton = $ui.inflate(
                        <button text="开始工作" w="*" h="40" id="startWorkDaTi"/>
                    , ui.containerAll);
                    // 将按钮添加到当前布局
                    ui.containerAll.addView(startButton);

                    // 设置“开始工作”按钮点击事件
                    startButton.setOnClickListener(() => {
                        //启动悬浮窗的代码，执行“融合代码”部分
                        if(!floatWindowFlag){
                            floatWindowFlag = true;
                            startWorkMulCount()
                        }else{
                            ui.run(() => {
                                toast("悬浮窗口已运行，请勿重复");
                            });
                        }
                        
                    });
                });
            } else {
                ui.run(() => {
                    toast("密钥验证失败: " + info.message);
                });
            }
        } catch (e) {
            // 请求出错
            console.log(e);
            ui.run(() => {
                toast("请求失败: " + e.message);
            });
        }
    });
});
/**
 * 功能: 解码 Unicode 字符串。
 * 
 * 该函数接收一个包含 Unicode 编码（例如 \\uXXXX）的字符串，并将其中的 Unicode 编码转为对应的字符。
 * 它使用正则表达式匹配字符串中的 Unicode 编码，并将其转换为字符后返回解码后的字符串。
 * 
 * 参数:
 * - str: 包含 Unicode 编码（如 \\uXXXX）的字符串。
 * 
 * 返回值:
 * - 返回一个解码后的字符串，Unicode 编码被转为对应的字符。
 * 
 * 示例:
 * ```
 * decodeUnicode("\\u4f60\\u597d"); // 返回 "你好"
 * ```
 */
function decodeUnicode(str) {
    return str.replace(/\\u([\dA-Fa-f]{4})/g, (match, code) => {
        return String.fromCharCode(parseInt(code, 16));
    });
}
//减去密钥使用次数
function startWorkMulCount(){
    let key = ui.name.text(); // 获取输入的密钥

    console.log("要扣除的次数的密钥ID",key);

    threads.start(() => {
        // 发送请求验证密钥
        let url = HostAddress + "";

        try {
            // 使用 http.postJson 发送请求，并在回调中处理响应
            var response = http.postJson(url, { keySecret: key });

            let info = response.body.json(); // 解析为 JSON 对象

            console.log("后端返回的信息:", info);
            // 判断后端是否返回成功
            if (info.success) {
                startFloatingWindow();
                let displayMessage = `\n次数: ${info.data.count} 次\n时长: ${info.data.duration} 天\n开通日期: ${info.data.generate_date}\n已使用次数: ${info.data.use_count}\n状态: ${info.message}`;
                ui.UserTextInfo.setText(displayMessage);
                //启动悬浮窗的代码，执行“融合代码”部分
                
            } else {
                if(info.data==0){
                    ui.run(() => {
                        toast("次数已用完,请联系客服充值");
                    });
                }else{
                    ui.run(() => {
                        toast("Error Command: " + info.message);
                    });
                }
            }
        } catch (e) {
            ui.run(() => {
                toast("Error Command: " + info.message);
            });
        }
    });
}
function startFloatingWindow() {
    ui.run(() => {
        toast("扣除一次使用次数");
    });
    //悬浮窗口答题主程序
    // 检查悬浮窗权限
    if (!floaty.checkPermission()) {
        toast("需要悬浮窗权限，请授权后重新运行");
        floaty.requestPermission();
        exit();
    }
    // 创建悬浮窗
    let window = floaty.rawWindow(
        <frame gravity="center" bg="#00FFFFFF"> 
            <vertical>
                <button id="start" text="开始/暂停识别答题" w="120" h="50" bg="#88FF5722" textColor="#FFFFFF" />
                <text text="--------------------------" textColor="#000000" textSize="12sp" h="10" />
                <scroll  w="*" h="100">
                    <text id="responseText" text="等待返回结果..." textColor="#000000" textSize="12sp" />
                </scroll>
                <text text="--------------------------" textColor="#000000" textSize="12sp"  h="10" />
                <button id="closeButton" text="关闭" w="120" h="40" bg="#88FF0000" textColor="#FFFFFF" /> 
            </vertical>
        </frame>
    );
    
    // 初始化悬浮窗位置
    window.setPosition(200, 200);
    window.setTouchable(true); // 设置悬浮窗可触摸
    
    // 定义变量用于拖动
    let x = 0, y = 0, wx = 0, wy = 0;
    
    let isMoving = false;
    
    let none_catch_check = [] // 不存在的题库记录
    
    let isAutoAnswering = false;  // 自动答题状态标志
    
    let count_order = 0;
    
    let style_type = "single";
    
    // 设置触摸监听
    window.start.setOnTouchListener((view, event) => {
        switch (event.getAction()) {
            case event.ACTION_DOWN:
                x = window.getX(); // 悬浮窗当前位置
                y = window.getY();
                wx = event.getRawX(); // 触摸点的 X 坐标
                wy = event.getRawY(); // 触摸点的 Y 坐标
                isMoving = false; // 初始化为非移动状态
                return true;
            case event.ACTION_MOVE:
                let dx = event.getRawX() - wx; // 移动的 X 距离
                let dy = event.getRawY() - wy; // 移动的 Y 距离
                if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
                    isMoving = true; // 识别为移动操作
                }
                // 更新悬浮窗位置
                ui.run(() => {
                    window.setPosition(x + dx, y + dy);
                });
                return true;
            case event.ACTION_UP:
                if (!isMoving) {
                    view.performClick(); // 如果不是移动操作，视为点击事件
                }
                return true;
        }
        return false;
    });
    
    // 点击“开始识别答题”按钮触发逻辑
    window.start.setOnClickListener(() => {
        threads.start(() => {
            isAutoAnswering = !isAutoAnswering
            sleep(1000)
            if(isAutoAnswering){
                toast("初始化中...");
                while(isAutoAnswering){
                    ui.run(() => window.responseText.setText("正在识别...")); // 必须在主线程更新 UI
                    let result = recognizeWithPaddleOCR();
                    if(result.style != "其他题"){
                        sendToBackend(result)
                    } else {
                        ui.run(() => window.responseText.setText("未能识别到内容")); // 在主线程更新 UI
                        click("下一题")
                        continue
                    }
                }
            }else{
                toast("初始化中...");
                ui.run(() => window.responseText.setText("已暂停，点击按钮继续")); // 必须在主线程更新 UI
            }
        });
    });
    
    // 点击“关闭”按钮时关闭悬浮窗并退出脚本
    window.closeButton.setOnClickListener(() => { // 使用 closeButton 而非 close
        isAutoAnswering = false
        none_catch_check = [] // 不存在的题库记录
        count_order = 0;
        style_type = "single";
        floatWindowFlag = false;
        window.close();
    });
    
    
    function formatOptions(input) {
        // 去掉 $ 前缀，并按顺序匹配选项
        let result = input.replace(/\$|O/g, ""); // 去掉 $ 和 O 前缀
        
        // 提取选项部分，并将它们按顺序排列
        let parts = result.match(/[A-D]\.[^A-D]*/g); // 匹配每个选项 "A.内容"
        
        if (!parts) return ""; // 如果没有匹配到任何选项，返回空字符串
    
        // 重新组合选项，去掉多余空格
        return parts.map(part => part.trim()).join("");
    }
    
    // 处理拼接文本函数
    function cleanResultText(input) {
       
    }
    /**
     * 判断是否在最后一页
     * return {style :"",result:""}
     * */
    // 界面识别
    function recognizeWithPaddleOCR() {
        try {
            // 判断交卷
            if(text("交卷").exists()){
                isAutoAnswering = false
                addAnswerTimes()
                return {style :"结束",result:"结束"}
            }
            // 获取页面上所有的 android.widget.TextView 控件
            var regionNome = "";
            var new_sentecnce = ""
            // 检查是否找到任何 TextView 控件
            if (regionNome.length > 0) {
                // 判断题型
                // 判断题型
                let style_type_area = "其他题"
                if (new_sentecnce.includes("单项选择题")) {
                    style_type_area = "选择题";
                    style_type = "single";
                } else if (new_sentecnce.includes("判断题")) {
                    style_type_area = "判断题";
                    style_type = "judge";
                } else if (new_sentecnce.includes("填空题")) {
                    style_type_area = "填空题";
                    style_type = "fill";
                }
                clean_setence = cleanResultText(new_sentecnce)
                //console.log("清洗之后的数据",style_type_area);
                return {style:style_type_area,result:clean_setence}
            } else {
                //console.log("没有找到任何 TextView 控件");
                return {style:"其他题",result:"暂无内容"}
            }
        }catch(e){
            toast("OCR 识别出错：" + e.message);
            return {style:"其他题",result:"暂无内容"}
        }
    }
    // 查找并点击包含指定文本的元素
    function clickElementContainingText(searchText) {
        // 使用 UiSelector 查找包含指定文本的元素
        let clickInfo = click(searchText)
        return clickInfo
    
    }
    // 发送题目信息结果到后端
    function sendToBackend(returnInfo) {
        //console.log("发送到后端的信息:", returnInfo);
        try {
            let url =  HostAddress + "";
            response = http.postJson(url, { result: returnInfo.result, style: returnInfo.style });
            ui.run(() => {
                count_order = count_order + 1
                if (response.statusCode == 200) {
                    let info = response.body.json(); // 解析为 JSON 对象
                    // 解码后端返回的 JSON 数据
                    //console.log("解码后的后端响应:", info);
                    let decodedMessage = decodeUnicode(info.data); // 解码 Unicode 字符
                    if(returnInfo.style != "填空题"){
                        var clickInfo = clickElementContainingText(decodedMessage)
                        if(clickInfo){
                            click("下一题")
                        }else{
                            var no_catch_info = {tixing:returnInfo.style,题号:count_order}
                            none_catch_check.push(no_catch_info)
                            click("下一题")
                        }
                    }else{
                        if(decodedMessage.includes("#")){
                            //多填空题策略
                            
                        }else{
                            if(decodedMessage=="暂无该题型"){
                                var no_catch_info = {tixing:returnInfo.style,题号:count_order}
                                none_catch_check.push(no_catch_info)
                            }if(decodedMessage!="暂无该题型"){
                                className("").find().setText(decodedMessage);
                            }
                            click("下一题")
                        }
                    }
                } else {
                    window.responseText.setText("发送失败，状态码：" + response.statusCode);
                    var no_catch_info = {tixing:style_type,题号:count_order}
                    none_catch_check.push(no_catch_info)
                    click("下一题")
                }
            });
        } catch (e) {
            ui.run(() => {
                window.responseText.setText("发送失败：" + e.message);
            });
            click("下一题")
        }
    }
    //填空题处理分割
    function processString(s) {
        // 用 # 进行分割，并过滤掉空字符串部分
        return s.split('#').filter(part => part !== '');
    }
    // Unicode 解码函数
    function decodeUnicode(str) {
        return str.replace(/\\u([\dA-Fa-f]{4})/g, (match, code) => {
            return String.fromCharCode(parseInt(code, 16));
        });
    }
    //对于准确率不符合有效答题机制的增加答题次数
    function addAnswerTimes() {
        var youxiao_answer_times = count_order*0.1
        if(none_catch_check.length > youxiao_answer_times){
            let key = ui.name.text(); // 获取输入的密钥
            console.log("要增加的次数的密钥ID",key);
            threads.start(() => {
                // 发送请求验证密钥
                let url =  HostAddress + "";
                try {
                    // 使用 http.postJson 发送请求，并在回调中处理响应
                    var response = http.postJson(url, { keySecret: key });
                    let info = response.body.json(); // 解析为 JSON 对象
                    //console.log("后端返回的信息:", info);
                    // 判断后端是否返回成功
                    if (info.success) {
                        ui.run(() => {
                            toast("无效答题，已返回扣除次数，2s后关闭");
                        });
                        sleep(2000);
                        window.close();
                    } else {
                        ui.run(() => {
                            toast("Error Command: " + info.message);
                        });
                        
                    }
                } catch (e) {
                    ui.run(() => {
                        toast("Error Command: " + info.message);
                    });
                }
            });
        }else{
            ui.run(() => {
                toast("有效答题，1s后关闭");
            });
            sleep(2000);
            window.close();
        }
        return;
    }
    // 保持脚本运行
    setInterval(() => {}, 1000);
}