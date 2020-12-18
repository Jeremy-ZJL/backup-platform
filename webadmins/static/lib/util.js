CMDB_HOST_INFORMATION="/api/cmdb/cmdb_host_information"
CMDB_STORAGE_INFORMATION='/api/cmdb/cmdb_storage_information'
BACKUP_HOST_MANAGER = '/api/backup/backup_host_manager'
SYS_ACCOUNT_LOGIN='/api/login/account_login'
BACKUP_DATABASE_MANAGER='/api/backup/backup_database_manager'
BACKUP_FS_MANAGER='/api/backup/backup_fs_manager'
BACKUP_POLICY_MANAGER='/api/backup/backup_policy_manager'
BACKUP_HISTORY_LIST='/api/backup/backup_history_list'
ACCOUNT_LOGIN_API = '/api/auth/login'
ACCOUNT_LOGOUT_API = '/api/auth/logout'
ACCOUNT_LOGIN_INFO = '/api/auth/account_login_info'
BACKUP_POLICY_SCHED_MANAGER = '/api/backup/backup_policy_sched_manager'
ACCOUNT_LOGIN_INFO="/api/auth/account_login_info"
ACCOUNT_CURRENT_USER='/api/auth/account_current_user'


function modalalertdemo(msg, interval=5000){
    $.Huimodalalert(msg ,interval)
}

function login_acquire(){
    var cookie = document.cookie;
    console.log('login_acquire - cookie : ', cookie, 'login_acquire - cookieType : ', typeof cookie);

    var re = /login=true/i;  // 正则表达式
    var login = cookie.search(re);  // 正则匹配，计算出cookie中是否有'login=true'
    /* cookie这个变量是string，所以可以使用search()方法
    search() 方法用于检索字符串中指定的子字符串，或检索与正则表达式相匹配的子字符串。
    如果没有找到任何匹配的子串，则返回 -1。 */
    // console.log('login_acquire - login : ', login);

    if (login === -1){  // 如果上面没有匹配到 'login=true', 则表示未登录，返回登录页面
        window.open("/static/login.html", '_self')
    }
}

function format_timestamp(timestamp) {  // 日期格式化
    let date = new Date(timestamp * 1000);  //时间戳为10位需*1000，时间戳为13位的话不需乘1000
    let Y = date.getFullYear() + '-';
    let M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
    let D = date.getDate() + ' ';
    let h = date.getHours() + ':';
    let m = (date.getMinutes() < 10 ? '0'  + date.getMinutes() : date.getMinutes()) + ':';
    let s = date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds();
    return Y+M+D+h+m+s;
}
    
function ajaxGet(url){
//不带参数的 ajaxget请求
    var result;
    $.ajax({
        url: url,
        type:"GET",
        async: false,
        success: function (args) {
            result=args
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            result = XMLHttpRequest.responseText
        },
    });
return result
}

function ajaxGet_data(url, data){
    // ajax GET请求
    //ajax带有参数的ajaxGET请求
    var result;
    $.ajax({
        data: data,
        url: url,
        type:"GET",
        async: false,
        success: function (args){
            result=args
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
             result = XMLHttpRequest.responseText
         },
    });
    return result
}

function ajaxPut(url, data, async=false){
    //ajax PUT请求
    var result;
    $.ajax({
        data:data,
        url:url,
        type:"PUT",
        async:async,
        success:function(msg){
                result =  msg;
        },

        error: function(XMLHttpRequest, textStatus, errorThrown) {
            result = XMLHttpRequest.responseText
         },

    });
    return result
}

function ajaxDelete(url, data){
    //ajax DELETE请求
    var result;
    $.ajax({
        data:data,
        url:url,
        type:"DELETE",
        async:false,
        success:function(msg){
            result =  msg;
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            result = XMLHttpRequest.responseText
            //modalalertdemo(msg);
         },

    });
    return result
}

function ajaxPost(url, data){
    //ajax POST请求
    var result;
    $.ajax({
        data:data,
        url:url,
        type:"POST",
        async:false,
        success:function(msg){
            result =  msg;
        },

        error: function(XMLHttpRequest, textStatus, errorThrown){
            result = XMLHttpRequest.responseText
         },

    });
    return result
}
