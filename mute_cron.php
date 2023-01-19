<?php
    $realdatetime_obj = new DateTime();
    $datetime = $realdatetime_obj->format("Y-m-d H:i");

    $connect = mysqli_connect("host", "user", "pass", "db");
    $results = mysqli_query($connect, "SELECT * FROM `mutes`");
    foreach($results as $result) {
        $db_datetime_obj = new DateTime("".$result["datetime"]);
        $db_datetime = $db_datetime_obj->format("Y-m-d H:i");
        if($datetime == $db_datetime) {
            $vk_id = $result["vk_id"];
            $db = mysqli_connect("host", "user", "pass", "db");
            mysqli_query($db, "DELETE FROM `mutes` WHERE `vk_id`='$vk_id'");
            mysqli_close($db);

            $request_params = array(
                'user_ids' => $result["vk_id"],
                'v' => '5.131',
                'access_token' => 'token'
            );

            $ch = curl_init("https://api.vk.com/method/users.get");
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $request_params);
            $response = curl_exec($ch);
            curl_close($ch);
            $response = json_decode($response, true)["response"][0];

            $vk_id = $result["vk_id"];
            $full_name = $response["first_name"] . " " . $response["last_name"];
            $name_src = "[id$vk_id|$full_name]";

            $request_params = array(
                'peer_id' => 2000000003,
                'message' => "$name_src, время вашего мута закончилось, теперь вы снова можете говорить",
                'random_id' => 0,
                'v' => '5.131',
                'access_token' => 'token'
            );
        
            $ch = curl_init("https://api.vk.com/method/messages.send");
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $request_params);
            curl_exec($ch);
            curl_close($ch);
        }
    }
?>