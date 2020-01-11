function ajaxDelete(url) {
    if (url=='') {
        alert('url is null');
        return false;
    }else{
        //alert(url);
        $.get(url,function(msg){
            alert(msg.info);
            if (msg.url!='' || msg.url!=undefined) {
                window.location.href=msg.url;
            }
            },'json').error(function(e){
            alert("ajax get was failed,status code is "+e.status);
            });
    }
}
var valiForm;
var kEditor;
function checkForm() {
    //check kindeditor content
    if (kEditor!=undefined && kEditor!=''&& kEditor!=null) {
		//alert("run to kindeditor");
        kEditor.sync();
        editorContent=$('#KE').val();
        if ($.trim(editorContent).length<=20) {
            //alert('article content is to short!');
            kEditor.focus();
			return false ;
        }
    }
    //check another input object
    $("form input[type='text']").each(function(){
        var val=$(this).val();
        var name=$(this).attr("name");
        if ($.trim(val).length==0) {
            alert('The '+name+" field value is empty!");
            $(this).focus();
            valiForm=false;
            return false;
        }else{
            valiForm=true;
        }
    });
}


function ajaxSubmit() {
    checkForm();
    //alert(valiForm);
    if (valiForm===false) {
        return;
    }
    url=$("#posturl").attr("value");
    data=$("form");
    if (url!=='') {
        $.post(
               url,
               data.serialize(),
               function (msg) {
                //alert(msg);
                alert(msg.info);
                if (msg.url!=='' && msg.url!==undefined) {
                    window.location.href=msg.url;
                }
               },
               "json"
               ).error(function(e){
            alert("ajax request is faile,error status"+e.status);
        });
    }else{
        alert("url is null");
    } 
}